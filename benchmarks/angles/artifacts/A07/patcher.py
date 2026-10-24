"""JSON Merge Patch (RFC 7386) with strict JSON-compatibility validation."""

import copy
import math


def _validate(value):
    """Raise ValueError unless value is an acyclic JSON-compatible value."""
    active = set()
    stack = [(value, False)]
    while stack:
        node, leaving = stack.pop()
        if leaving:
            active.discard(id(node))
            continue
        if node is None or isinstance(node, (bool, int, str)):
            continue
        if isinstance(node, float):
            if not math.isfinite(node):
                raise ValueError("non-finite floats are not JSON-compatible")
            continue
        if isinstance(node, list):
            if id(node) in active:
                raise ValueError("cyclic values are not JSON-compatible")
            active.add(id(node))
            stack.append((node, True))
            stack.extend((item, False) for item in node)
            continue
        if isinstance(node, dict):
            if id(node) in active:
                raise ValueError("cyclic values are not JSON-compatible")
            active.add(id(node))
            stack.append((node, True))
            for key, item in node.items():
                if not isinstance(key, str):
                    raise ValueError("JSON object keys must be strings")
                stack.append((item, False))
            continue
        raise ValueError("value is not JSON-compatible")


def merge_patch(document, patch):
    """Merge patch into a deep copy of document without mutating either input."""
    _validate(document)
    _validate(patch)
    if not isinstance(patch, dict):
        return copy.deepcopy(patch)

    result = copy.deepcopy(document) if isinstance(document, dict) else {}
    pending = [(result, patch)]
    while pending:
        target, changes = pending.pop()
        for key, value in changes.items():
            if value is None:
                target.pop(key, None)
            elif isinstance(value, dict):
                existing = target.get(key)
                base = copy.deepcopy(existing) if isinstance(existing, dict) else {}
                target[key] = base
                pending.append((base, value))
            else:
                target[key] = copy.deepcopy(value)
    return result
