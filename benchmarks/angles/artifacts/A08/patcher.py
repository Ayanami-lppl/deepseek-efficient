import math


def _copy(value):
    """Validate a JSON-compatible value and return an independent deep copy."""
    if value is None or isinstance(value, bool) or isinstance(value, int):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return value
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return [_copy(item) for item in value]
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("non-string dict key")
            result[key] = _copy(item)
        return result
    raise ValueError("unsupported value type: %r" % (type(value).__name__,))


def _merge(target, patch):
    for key, value in patch.items():
        if value is None:
            target.pop(key, None)
        elif isinstance(value, dict):
            current = target.get(key)
            if not isinstance(current, dict):
                current = {}
            target[key] = _merge(current, value)
        else:
            target[key] = value
    return target


def merge_patch(document, patch):
    document_copy = _copy(document)
    patch_copy = _copy(patch)
    if not isinstance(patch_copy, dict):
        return patch_copy
    if not isinstance(document_copy, dict):
        document_copy = {}
    return _merge(document_copy, patch_copy)
