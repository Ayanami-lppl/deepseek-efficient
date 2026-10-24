import copy
import math


def _validate(value, seen):
    kind = type(value)
    if value is None or kind is bool or kind is int or kind is str:
        return
    if kind is float:
        if not math.isfinite(value):
            raise ValueError("non-finite float")
        return
    if kind not in (list, dict):
        raise ValueError("non-JSON value: %r" % (kind,))
    marker = id(value)
    if marker in seen:
        raise ValueError("cyclic value")
    seen.add(marker)
    if kind is list:
        for item in value:
            _validate(item, seen)
    else:
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError("non-string key")
            _validate(item, seen)
    seen.discard(marker)


def _merge(target, patch):
    for key, value in patch.items():
        if value is None:
            target.pop(key, None)
        elif type(value) is dict:
            current = target.get(key)
            if type(current) is not dict:
                current = {}
                target[key] = current
            _merge(current, value)
        elif type(value) is list:
            target[key] = copy.deepcopy(value)
        else:
            target[key] = value


def merge_patch(document, patch):
    seen = set()
    _validate(document, seen)
    _validate(patch, seen)
    if type(patch) is not dict:
        return copy.deepcopy(patch)
    target = copy.deepcopy(document) if type(document) is dict else {}
    _merge(target, patch)
    return target
