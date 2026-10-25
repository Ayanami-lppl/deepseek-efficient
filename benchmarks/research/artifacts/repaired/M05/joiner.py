import copy


def _validate_row(row, key):
    if not isinstance(row, dict):
        raise ValueError('row must be a dict')
    for name in row:
        if not isinstance(name, str) or not name:
            raise ValueError('field names must be non-empty str')
    if key not in row:
        raise ValueError('row must contain the join key')
    value = row[key]
    if not isinstance(value, str) or not value:
        raise ValueError('join value must be a non-empty str')


def left_join(left, right, key):
    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError('left and right must be lists')
    if not isinstance(key, str) or not key:
        raise ValueError('key must be a non-empty str')

    index = {}
    columns = []
    seen = set()
    for row in right:
        _validate_row(row, key)
        value = row[key]
        if value in index:
            raise ValueError('duplicate right join value')
        index[value] = row
        for name in row:
            if name != key and name not in seen:
                seen.add(name)
                columns.append(name)

    for row in left:
        _validate_row(row, key)

    generated = ['right.' + name for name in columns]
    for row in left:
        for name in generated:
            if name in row:
                raise ValueError('left row already has a generated column')

    result = []
    for row in left:
        out = {name: copy.deepcopy(value) for name, value in row.items()}
        match = index.get(row[key])
        for name, column in zip(columns, generated):
            if match is not None and name in match:
                out[column] = copy.deepcopy(match[name])
            else:
                out[column] = None
        result.append(out)
    return result
