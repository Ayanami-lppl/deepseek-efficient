import copy
import math


def _validate(value, active):
    if value is None or isinstance(value, (bool, str)):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float is not JSON-compatible")
        return
    if isinstance(value, (list, dict)):
        if id(value) in active:
            raise ValueError("circular reference is not JSON-compatible")
        active.add(id(value))
        try:
            if isinstance(value, list):
                for item in value:
                    _validate(item, active)
            else:
                for key, item in value.items():
                    if not isinstance(key, str):
                        raise ValueError("dict keys must be strings")
                    _validate(item, active)
        finally:
            active.remove(id(value))
        return
    raise ValueError("unsupported value: %r" % (type(value),))


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
    return target


def merge_patch(document, patch):
    _validate(document, set())
    _validate(patch, set())
    if not isinstance(patch, dict):
        return copy.deepcopy(patch)
    target = copy.deepcopy(document) if isinstance(document, dict) else {}
    return _merge(target, patch)
