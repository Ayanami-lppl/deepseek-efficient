import copy


def _validate_key(key):
    if not isinstance(key, str) or not key:
        raise ValueError("key must be a non-empty str")


def _validate_row(row, key):
    if not isinstance(row, dict):
        raise ValueError("each row must be a dict")
    for name in row:
        if not isinstance(name, str) or not name:
            raise ValueError("field names must be non-empty str")
    if key not in row:
        raise ValueError("each row must contain the join key")
    value = row[key]
    if not isinstance(value, str) or not value:
        raise ValueError("join values must be non-empty str")
    try:
        copy.deepcopy(row)
    except Exception as exc:
        raise ValueError("row is not deep-copyable") from exc


def left_join(left, right, key):
    _validate_key(key)
    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError("left and right must be lists")

    for row in left:
        _validate_row(row, key)
    for row in right:
        _validate_row(row, key)

    index = {}
    columns = []
    seen = set()
    for row in right:
        value = row[key]
        if value in index:
            raise ValueError("right join values must be unique")
        index[value] = row
        for name in row:
            if name != key and name not in seen:
                seen.add(name)
                columns.append((name, "right." + name))

    left_fields = {name for row in left for name in row}
    for _, output_name in columns:
        if output_name in left_fields:
            raise ValueError("prefix collision: " + output_name)

    result = []
    for row in left:
        output = copy.deepcopy(row)
        match = index.get(row[key])
        for name, output_name in columns:
            if match is not None and name in match:
                output[output_name] = copy.deepcopy(match[name])
            else:
                output[output_name] = None
        result.append(output)
    return result
