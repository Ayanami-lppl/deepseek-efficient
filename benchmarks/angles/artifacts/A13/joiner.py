import copy


def _valid_rows(rows, key):
    for row in rows:
        if not isinstance(row, dict) or key not in row:
            raise ValueError("invalid row")
        for name in row:
            if not isinstance(name, str) or not name:
                raise ValueError("invalid field name")
        value = row[key]
        if not isinstance(value, str) or not value:
            raise ValueError("invalid join value")


def left_join(left, right, key):
    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError("left and right must be lists")
    if not isinstance(key, str) or not key:
        raise ValueError("key must be a non-empty str")

    _valid_rows(left, key)
    _valid_rows(right, key)

    index = {}
    columns = []
    for row in right:
        value = row[key]
        if value in index:
            raise ValueError("duplicate right join value")
        index[value] = row
        for name in row:
            if name != key:
                column = "right." + name
                if column not in columns:
                    columns.append(column)

    if columns:
        generated = set(columns)
        for row in left:
            if generated.intersection(row):
                raise ValueError("prefix column collision")

    pairs = [(column, column[len("right."):]) for column in columns]
    result = []
    for row in left:
        out = copy.deepcopy(row)
        match = index.get(row[key])
        for column, name in pairs:
            if match is not None and name in match:
                out[column] = copy.deepcopy(match[name])
            else:
                out[column] = None
        result.append(out)
    return result
