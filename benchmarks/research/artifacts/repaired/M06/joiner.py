import copy


def left_join(left, right, key):
    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError('left and right must be lists')
    if not isinstance(key, str) or not key:
        raise ValueError('key must be a non-empty string')

    def validate(rows, side):
        for row in rows:
            if not isinstance(row, dict):
                raise ValueError('%s rows must be dicts' % side)
            for name in row:
                if not isinstance(name, str) or not name:
                    raise ValueError('field names must be non-empty strings')
            if key not in row:
                raise ValueError('%s row is missing key' % side)
            value = row[key]
            if not isinstance(value, str) or not value:
                raise ValueError('join values must be non-empty strings')

    validate(left, 'left')
    validate(right, 'right')

    columns = []
    seen_columns = set()
    index = {}
    for row in right:
        value = row[key]
        if value in index:
            raise ValueError('duplicate right key')
        index[value] = row
        for name in row:
            if name != key and name not in seen_columns:
                seen_columns.add(name)
                columns.append(name)

    prefixed = [('right.' + name, name) for name in columns]
    for row in left:
        for out_name, _ in prefixed:
            if out_name in row:
                raise ValueError('left row already contains prefixed column')

    result = []
    for row in left:
        out = copy.deepcopy(row)
        matched = index.get(row[key])
        for out_name, name in prefixed:
            if matched is not None and name in matched:
                out[out_name] = copy.deepcopy(matched[name])
            else:
                out[out_name] = None
        result.append(out)
    return result
