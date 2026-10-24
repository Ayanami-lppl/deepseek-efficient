import copy
import math


def _validate(value, stack):
    if value is None or isinstance(value, (bool, int, str)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float is not allowed")
        return
    if isinstance(value, list):
        if id(value) in stack:
            raise ValueError("cyclic value is not allowed")
        stack.add(id(value))
        for item in value:
            _validate(item, stack)
        stack.discard(id(value))
        return
    if isinstance(value, dict):
        if id(value) in stack:
            raise ValueError("cyclic value is not allowed")
        stack.add(id(value))
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("dict keys must be strings")
            _validate(item, stack)
        stack.discard(id(value))
        return
    raise ValueError("unsupported value type: %r" % (type(value),))


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
