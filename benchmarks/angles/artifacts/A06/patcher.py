import math


def _validate(value, stack=None):
    if stack is None:
        stack = set()
    if value is None or isinstance(value, bool):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return
    if isinstance(value, str):
        return
    if isinstance(value, (list, dict)):
        if id(value) in stack:
            raise ValueError("cyclic value")
        stack.add(id(value))
        try:
            if isinstance(value, list):
                for item in value:
                    _validate(item, stack)
            else:
                for key, item in value.items():
                    if not isinstance(key, str):
                        raise ValueError("non-string dict key")
                    _validate(item, stack)
        finally:
            stack.remove(id(value))
        return
    raise ValueError("unsupported type: %r" % (type(value),))


def _copy(value):
    if isinstance(value, list):
        return [_copy(item) for item in value]
    if isinstance(value, dict):
        return {key: _copy(item) for key, item in value.items()}
    return value


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
            target[key] = _copy(value)
    return target


def merge_patch(document, patch):
    _validate(document)
    _validate(patch)
    patch_copy = _copy(patch)
    if not isinstance(patch_copy, dict):
        return patch_copy
    if isinstance(document, dict):
        target = _copy(document)
    else:
        target = {}
    return _merge(target, patch_copy)
