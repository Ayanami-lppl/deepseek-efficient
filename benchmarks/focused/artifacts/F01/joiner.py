import copy


def _copy(value):
    return copy.deepcopy(value)


def _validate_rows(rows, key, side):
    if not isinstance(rows, list):
        raise ValueError('%s must be a list' % side)
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('%s rows must be dicts' % side)
        for name in row:
            if not isinstance(name, str) or not name:
                raise ValueError('%s field names must be non-empty str' % side)
        if key not in row:
            raise ValueError('%s row missing key %r' % (side, key))
        value = row[key]
        if not isinstance(value, str) or not value:
            raise ValueError('%s join value must be non-empty str' % side)


def left_join(left, right, key):
    if not isinstance(key, str) or not key:
        raise ValueError('key must be a non-empty str')
    _validate_rows(left, key, 'left')
    _validate_rows(right, key, 'right')

    columns = []
    seen = set()
    index = {}
    for row in right:
        value = row[key]
        if value in index:
            raise ValueError('duplicate right join value %r' % value)
        index[value] = row
        for name in row:
            if name != key and name not in seen:
                seen.add(name)
                columns.append('right.' + name)

    generated = set(columns)
    for row in left:
        if generated.intersection(row):
            raise ValueError('left row already contains a generated column')

    result = []
    for row in left:
        out = {name: _copy(value) for name, value in row.items()}
        match = index.get(row[key])
        for column in columns:
            name = column[len('right.'):]
            if match is not None and name in match:
                out[column] = _copy(match[name])
            else:
                out[column] = None
        result.append(out)
    return result
