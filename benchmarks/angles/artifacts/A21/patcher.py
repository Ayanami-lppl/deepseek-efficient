import copy
import math


def _validate(value, active=None, validated=None):
    """Reject values that are not acyclic, JSON-compatible values."""
    if value is None or isinstance(value, (bool, str)):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite float is not a valid value")
        return
    if not isinstance(value, (list, dict)):
        raise ValueError("unsupported value type: %s" % type(value).__name__)

    value_id = id(value)
    if active is None:
        active = set()
    if validated is None:
        validated = set()
    if value_id in active:
        raise ValueError("cyclic value is not supported")
    if value_id in validated:
        return

    active.add(value_id)
    try:
        if isinstance(value, list):
            for item in value:
                _validate(item, active, validated)
        else:
            for key, item in value.items():
                if not isinstance(key, str):
                    raise ValueError("dictionary keys must be strings")
                _validate(item, active, validated)
    finally:
        active.remove(value_id)
    validated.add(value_id)


def _merge_object(target, patch):
    for key, value in patch.items():
        if value is None:
            target.pop(key, None)
        elif isinstance(value, dict):
            current = target.get(key)
            if not isinstance(current, dict):
                current = {}
                target[key] = current
            _merge_object(current, value)
        else:
            target[key] = copy.deepcopy(value)
    return target


def merge_patch(document, patch):
    _validate(document)
    _validate(patch)

    if not isinstance(patch, dict):
        return copy.deepcopy(patch)

    target = copy.deepcopy(document) if isinstance(document, dict) else {}
    return _merge_object(target, patch)
