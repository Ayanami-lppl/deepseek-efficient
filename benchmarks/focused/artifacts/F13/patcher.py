import copy
import math


def _validate(value, active):
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, str):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float is not JSON compatible")
        return
    if isinstance(value, (list, dict)):
        if id(value) in active:
            raise ValueError("cyclic value is not JSON compatible")
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
            active.discard(id(value))
        return
    raise ValueError("value is not JSON compatible: %r" % (type(value).__name__,))


def _merge(target, patch):
    for key, value in patch.items():
        if value is None:
            target.pop(key, None)
        elif isinstance(value, dict):
            base = target.get(key)
            if not isinstance(base, dict):
                base = {}
            target[key] = _merge(base, value)
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
