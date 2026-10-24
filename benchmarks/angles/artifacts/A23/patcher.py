import math


def _validate(value, active=None):
    if active is None:
        active = set()
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
        ident = id(value)
        if ident in active:
            raise ValueError("cyclic value")
        active.add(ident)
        if isinstance(value, list):
            for item in value:
                _validate(item, active)
        else:
            for key, item in value.items():
                if not isinstance(key, str):
                    raise ValueError("non-string dict key")
                _validate(item, active)
        active.remove(ident)
        return
    raise ValueError("unsupported value type")


def _merge(target, patch):
    for key, value in patch.items():
        if value is None:
            target.pop(key, None)
        elif isinstance(value, dict):
            if not isinstance(target.get(key), dict):
                target[key] = {}
            _merge(target[key], value)
        else:
            target[key] = _deep_copy(value)
    return target


def _deep_copy(value):
    if isinstance(value, list):
        return [_deep_copy(item) for item in value]
    if isinstance(value, dict):
        return {key: _deep_copy(item) for key, item in value.items()}
    return value


def merge_patch(document, patch):
    _validate(document)
    _validate(patch)
    if not isinstance(patch, dict):
        return _deep_copy(patch)
    target = _deep_copy(document) if isinstance(document, dict) else {}
    return _merge(target, patch)
