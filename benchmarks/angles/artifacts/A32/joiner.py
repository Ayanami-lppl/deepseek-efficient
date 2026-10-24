import copy


_PREFIX = 'right.'


def _validate(rows, key):
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('each row must be a dict')
        for name in row:
            if not isinstance(name, str) or not name:
                raise ValueError('field names must be non-empty str')
        if key not in row:
            raise ValueError('row is missing join key')
        value = row[key]
        if not isinstance(value, str) or not value:
            raise ValueError('join values must be non-empty str')


def left_join(left, right, key):
    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError('left and right must be lists')
    if not isinstance(key, str) or not key:
        raise ValueError('key must be a non-empty str')

    _validate(left, key)
    _validate(right, key)

    index = {}
    for row in right:
        value = row[key]
        if value in index:
            raise ValueError('duplicate right join value')
        index[value] = row

    columns = []
    seen = set()
    for row in right:
        for name in row:
            if name != key and name not in seen:
                seen.add(name)
                columns.append(_PREFIX + name)

    for row in left:
        for column in columns:
            if column in row:
                raise ValueError('right prefix column would overwrite left field')

    result = []
    try:
        for row in left:
            out = {name: copy.deepcopy(value) for name, value in row.items()}
            match = index.get(row[key])
            for column in columns:
                name = column[len(_PREFIX):]
                if match is not None and name in match:
                    out[column] = copy.deepcopy(match[name])
                else:
                    out[column] = None
            result.append(out)
    except Exception as error:
        raise ValueError('values must be deep-copyable') from error
    return result
