import copy


def _validate_rows(rows, key, side):
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(f"{side} rows must be dicts")
        for name in row:
            if not isinstance(name, str) or not name:
                raise ValueError("field names must be non-empty strings")
        if key not in row:
            raise ValueError(f"{side} rows must contain the join key")
        value = row[key]
        if not isinstance(value, str) or not value:
            raise ValueError("join values must be non-empty strings")


def _copy_value(value, what):
    try:
        return copy.deepcopy(value)
    except Exception as exc:
        raise ValueError(f"{what} is not deep-copyable") from exc


def left_join(left, right, key):
    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError("left and right must be lists")
    if not isinstance(key, str) or not key:
        raise ValueError("key must be a non-empty string")

    _validate_rows(left, key, "left")
    _validate_rows(right, key, "right")

    index = {}
    right_columns = {}
    for row in right:
        value = row[key]
        if value in index:
            raise ValueError("right join values must be unique")
        index[value] = row
        for name in row:
            if name != key:
                right_columns.setdefault(name, None)

    generated = ["right." + name for name in right_columns]
    for row in left:
        for name in generated:
            if name in row:
                raise ValueError(f"left row already contains {name!r}")

    result = []
    for row in left:
        out = _copy_value(row, "left row")
        match = index.get(row[key])
        for name in right_columns:
            out_name = "right." + name
            if match is not None and name in match:
                out[out_name] = _copy_value(match[name], "right value")
            else:
                out[out_name] = None
        result.append(out)
    return result
