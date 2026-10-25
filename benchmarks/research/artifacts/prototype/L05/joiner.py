import copy


def _check_row(row, key):
    if not isinstance(row, dict):
        raise ValueError('row must be a dict')
    for name in row:
        if not isinstance(name, str) or not name:
            raise ValueError('field names must be non-empty str')
    if key not in row:
        raise ValueError('row is missing the join key')
    value = row[key]
    if not isinstance(value, str) or not value:
        raise ValueError('join values must be non-empty str')


def left_join(left, right, key):
    if not isinstance(key, str) or not key:
        raise ValueError('key must be a non-empty str')
    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError('left and right must be lists')

    for row in right:
        _check_row(row, key)

    right_columns = []
    seen_columns = set()
    index = {}
    for row in right:
        value = row[key]
        if value in index:
            raise ValueError('duplicate right join value')
        index[value] = row
        for name in row:
            if name != key and name not in seen_columns:
                seen_columns.add(name)
                right_columns.append(name)

    for row in left:
        _check_row(row, key)

    prefixed = ['right.' + name for name in right_columns]
    for row in left:
        for name in prefixed:
            if name in row:
                raise ValueError('left row already contains ' + name)

    result = []
    for row in left:
        out = {name: copy.deepcopy(value) for name, value in row.items()}
        match = index.get(row[key])
        for name, prefixed_name in zip(right_columns, prefixed):
            if match is not None and name in match:
                out[prefixed_name] = copy.deepcopy(match[name])
            else:
                out[prefixed_name] = None
        result.append(out)
    return result
