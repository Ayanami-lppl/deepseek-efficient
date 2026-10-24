import copy


def _invalid(message):
    raise ValueError(message)


def _copy(value):
    try:
        return copy.deepcopy(value)
    except Exception:
        raise ValueError("row value cannot be deep-copied") from None


def _validate_rows(rows, key, side):
    seen = set()
    for row in rows:
        if not isinstance(row, dict):
            _invalid(f"{side} row must be a dict")
        for name in row:
            if not isinstance(name, str) or not name:
                _invalid(f"{side} row field names must be non-empty str")
        if key not in row:
            _invalid(f"{side} row missing join key")
        value = row[key]
        if not isinstance(value, str) or not value:
            _invalid(f"{side} join value must be a non-empty str")
        if side == "right":
            if value in seen:
                _invalid("duplicate right join value")
            seen.add(value)


def left_join(left, right, key):
    if not isinstance(left, list) or not isinstance(right, list):
        _invalid("left and right must be lists")
    if not isinstance(key, str) or not key:
        _invalid("key must be a non-empty str")

    _validate_rows(left, key, "left")
    _validate_rows(right, key, "right")

    columns = []
    seen_columns = set()
    for row in right:
        for name in row:
            if name != key and name not in seen_columns:
                seen_columns.add(name)
                columns.append(name)

    generated = {"right." + name for name in columns}
    for row in left:
        if generated.intersection(row):
            _invalid("left row already contains a generated right column")

    index = {}
    for row in right:
        index[row[key]] = row

    result = []
    for row in left:
        out = _copy(row)
        match = index.get(row[key])
        for name in columns:
            out["right." + name] = _copy(match[name]) if match is not None and name in match else None
        result.append(out)
    return result
