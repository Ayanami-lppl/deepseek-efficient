import copy
import math


def _validate(value):
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float is not JSON compatible")
        return
    if isinstance(value, str):
        return
    if isinstance(value, list):
        for item in value:
            _validate(item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("dict keys must be strings")
            _validate(item)
        return
    raise ValueError("unsupported value type: %r" % (type(value).__name__,))


def _merge(document, patch):
    target = copy.deepcopy(document) if isinstance(document, dict) else {}
    for key, value in patch.items():
        if value is None:
            target.pop(key, None)
        elif isinstance(value, dict):
            target[key] = _merge(target.get(key), value)
        else:
            target[key] = copy.deepcopy(value)
    return target


def merge_patch(document, patch):
    _validate(document)
    _validate(patch)
    if not isinstance(patch, dict):
        return copy.deepcopy(patch)
    return _merge(document, patch)
