import copy
import math


def _validate(value):
    if value is None or isinstance(value, (bool, str)):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float is not JSON compatible")
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
    raise ValueError("unsupported value: %r" % (type(value).__name__,))


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
            target[key] = copy.deepcopy(value)


def merge_patch(document, patch):
    _validate(document)
    _validate(patch)
    if not isinstance(patch, dict):
        return copy.deepcopy(patch)
    target = copy.deepcopy(document) if isinstance(document, dict) else {}
    _merge(target, patch)
    return target
