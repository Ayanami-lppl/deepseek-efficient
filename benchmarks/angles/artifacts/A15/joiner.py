import copy

_PREFIX = "right."


def _invalid(message):
    raise ValueError(message)


def _copy(value):
    try:
        return copy.deepcopy(value)
    except Exception:
        _invalid("value is not deep-copyable")


def _validate(rows, key, side):
    if not isinstance(rows, list):
        _invalid("%s must be a list of dicts" % side)
    for row in rows:
        if not isinstance(row, dict):
            _invalid("%s row must be a dict" % side)
        for name in row:
            if not isinstance(name, str) or not name:
                _invalid("%s field name must be a non-empty str" % side)
        if key not in row:
            _invalid("%s row is missing the join key" % side)
        value = row[key]
        if not isinstance(value, str) or not value:
            _invalid("%s join value must be a non-empty str" % side)


def left_join(left, right, key):
    if not isinstance(key, str) or not key:
        _invalid("key must be a non-empty str")
    _validate(left, key, "left")
    _validate(right, key, "right")

    index = {}
    columns = []
    seen = set()
    for row in right:
        value = row[key]
        if value in index:
            _invalid("duplicate join value in right rows")
        index[value] = row
        for name in row:
            if name != key and name not in seen:
                seen.add(name)
                columns.append(name)

    prefixed = {_PREFIX + name for name in columns}
    for row in left:
        for name in row:
            if name in prefixed:
                _invalid("left row already has a generated column name")

    result = []
    for row in left:
        merged = {}
        for name, value in row.items():
            merged[name] = _copy(value)
        match = index.get(row[key])
        for name in columns:
            if match is not None and name in match:
                merged[_PREFIX + name] = _copy(match[name])
            else:
                merged[_PREFIX + name] = None
        result.append(merged)
    return result
