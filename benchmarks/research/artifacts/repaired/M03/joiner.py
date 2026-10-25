import copy


def left_join(left, right, key):
    if not isinstance(key, str) or not key:
        raise ValueError("key must be a non-empty string")
    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError("left and right must be lists of dicts")

    def check_row(row):
        if not isinstance(row, dict):
            raise ValueError("each row must be a dict")
        for name in row:
            if not isinstance(name, str) or not name:
                raise ValueError("field names must be non-empty strings")
        if key not in row:
            raise ValueError("every row must contain the key")
        value = row[key]
        if not isinstance(value, str) or not value:
            raise ValueError("key values must be non-empty strings")

    index = {}
    columns = []
    seen_columns = set()
    for row in right:
        check_row(row)
        value = row[key]
        if value in index:
            raise ValueError("right key values must be unique")
        index[value] = row
        for name in row:
            if name != key and name not in seen_columns:
                seen_columns.add(name)
                columns.append(name)

    generated = {"right." + name for name in columns}
    for row in left:
        check_row(row)
        if generated.intersection(row):
            raise ValueError("left row already contains a generated column name")

    result = []
    for row in left:
        out = copy.deepcopy(row)
        match = index.get(row[key])
        for name in columns:
            if match is not None and name in match:
                out["right." + name] = copy.deepcopy(match[name])
            else:
                out["right." + name] = None
        result.append(out)
    return result
