import copy


def left_join(left, right, key):
    if not isinstance(key, str) or not key:
        raise ValueError('key must be a non-empty str')
    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError('left and right must be lists')

    def check(row):
        if not isinstance(row, dict):
            raise ValueError('rows must be dicts')
        for name in row:
            if not isinstance(name, str) or not name:
                raise ValueError('field names must be non-empty str')
        if key not in row:
            raise ValueError('every row must contain the key')
        value = row[key]
        if not isinstance(value, str) or not value:
            raise ValueError('join values must be non-empty str')

    for row in left:
        check(row)
    for row in right:
        check(row)

    columns = []
    index = {}
    for row in right:
        value = row[key]
        if value in index:
            raise ValueError('right join values must be unique')
        index[value] = row
        for name in row:
            if name != key:
                column = 'right.' + name
                if column not in columns:
                    columns.append(column)

    for row in left:
        for column in columns:
            if column in row:
                raise ValueError('output column would overwrite a left field')

    result = []
    for row in left:
        out = {name: copy.deepcopy(value) for name, value in row.items()}
        match = index.get(row[key])
        for name in columns:
            if match is not None and name[len('right.'):] in match:
                out[name] = copy.deepcopy(match[name[len('right.'):]])
            else:
                out[name] = None
        result.append(out)
    return result
