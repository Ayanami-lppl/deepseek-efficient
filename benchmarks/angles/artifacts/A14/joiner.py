import copy


def left_join(left, right, key):
    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError("left and right must be lists")
    if not isinstance(key, str) or not key:
        raise ValueError("key must be a non-empty string")

    def validate_rows(rows):
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError("each row must be a dict")
            for name in row:
                if not isinstance(name, str) or not name:
                    raise ValueError("field names must be non-empty strings")
            if key not in row:
                raise ValueError("every row must contain the key")
            value = row[key]
            if not isinstance(value, str) or not value:
                raise ValueError("join values must be non-empty strings")

    validate_rows(left)
    validate_rows(right)

    right_columns = []
    seen_columns = set()
    index = {}
    for row in right:
        value = row[key]
        if value in index:
            raise ValueError("duplicate right join value")
        index[value] = row
        for name in row:
            if name != key and name not in seen_columns:
                seen_columns.add(name)
                right_columns.append(name)

    columns = ["right." + name for name in right_columns]
    for row in left:
        for column in columns:
            if column in row:
                raise ValueError("left row already contains output column " + column)

    def clone(value):
        try:
            return copy.deepcopy(value)
        except Exception as exc:
            raise ValueError("values must be deep-copyable") from exc

    result = []
    for row in left:
        output = {name: clone(value) for name, value in row.items()}
        match = index.get(row[key])
        for name, column in zip(right_columns, columns):
            if match is not None and name in match:
                output[column] = clone(match[name])
            else:
                output[column] = None
        result.append(output)
    return result
