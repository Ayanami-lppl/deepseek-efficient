"""JSON Merge Patch implementation (RFC 7386) over strict JSON values."""

import math


def _copy_json(value, memo=None, active=None):
    """Validate a JSON-compatible value and return an independent deep copy.

    Raises ValueError for tuples, sets, non-string dict keys, NaN/Infinity,
    unsupported types, and cycles.
    """
    if memo is None:
        memo = {}
    if active is None:
        active = set()

    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return int(value)
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float is not a JSON value")
        return float(value)
    if isinstance(value, str):
        return value

    is_list = isinstance(value, list)
    is_dict = isinstance(value, dict)
    if not (is_list or is_dict):
        raise ValueError("unsupported JSON value: %r" % (type(value),))

    marker = id(value)
    if marker in active:
        raise ValueError("cyclic value is not a JSON value")
    if marker in memo:
        return memo[marker]

    active.add(marker)
    try:
        if is_list:
            result = []
            memo[marker] = result
            for item in value:
                result.append(_copy_json(item, memo, active))
            return result

        result = {}
        memo[marker] = result
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("non-string dict key is not a JSON value")
            result[key] = _copy_json(item, memo, active)
        return result
    finally:
        active.discard(marker)


def _merge(target, patch):
    for key, value in patch.items():
        if value is None:
            target.pop(key, None)
        elif isinstance(value, dict):
            current = target.get(key)
            if not isinstance(current, dict):
                current = {}
                target[key] = current
            _merge(current, value)
        else:
            target[key] = value


def merge_patch(document, patch):
    """Apply *patch* to *document* per the merge-patch semantics."""
    doc = _copy_json(document)
    pat = _copy_json(patch)

    if not isinstance(pat, dict):
        return pat

    target = doc if isinstance(doc, dict) else {}
    _merge(target, pat)
    return target
