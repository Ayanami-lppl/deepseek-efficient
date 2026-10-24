import copy


def _validate_rows(rows, key):
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("each row must be a dict")
        for name in row:
            if not isinstance(name, str) or not name:
                raise ValueError("field names must be non-empty strings")
        if key not in row:
            raise ValueError("each row must contain the join key")
        value = row[key]
        if not isinstance(value, str) or not value:
            raise ValueError("join values must be non-empty strings")


def left_join(left, right, key):
    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError("left and right must be lists")
    if not isinstance(key, str) or not key:
        raise ValueError("key must be a non-empty string")

    _validate_rows(left, key)
    _validate_rows(right, key)

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
                columns.append(name)

    prefixed = ["right." + name for name in columns]
    for row in left:
        for name in prefixed:
            if name in row:
                raise ValueError("prefixed column would overwrite a left field")

    result = []
    for left_row in left:
        output = copy.deepcopy(left_row)
        right_row = index.get(left_row[key])
        for name, output_name in zip(columns, prefixed):
            if right_row is not None and name in right_row:
                output[output_name] = copy.deepcopy(right_row[name])
            else:
                output[output_name] = None
        result.append(output)
    return result
