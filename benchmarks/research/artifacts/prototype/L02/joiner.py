import copy

PREFIX = 'right.'


def _check_rows(rows, key):
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('row must be a dict')
        for field in row:
            if not isinstance(field, str) or not field:
                raise ValueError('field names must be non-empty strings')
        if key not in row:
            raise ValueError('row missing key')
        value = row[key]
        if not isinstance(value, str) or not value:
            raise ValueError('join value must be a non-empty string')


def left_join(left, right, key):
    if not isinstance(key, str) or not key:
        raise ValueError('key must be a non-empty string')
    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError('left and right must be lists')
    _check_rows(left, key)
    _check_rows(right, key)

    right_fields = []
    seen = set()
    for row in right:
        for field in row:
            if field != key and field not in seen:
                seen.add(field)
                right_fields.append(field)
    prefixed = [PREFIX + field for field in right_fields]

    index = {}
    for row in right:
        value = row[key]
        if value in index:
            raise ValueError('duplicate right join value')
        index[value] = row

    if prefixed:
        generated = set(prefixed)
        for row in left:
            if any(field in generated for field in row):
                raise ValueError('left row already contains generated column')

    result = []
    for row in left:
        out = copy.deepcopy(row)
        match = index.get(row[key])
        for field, name in zip(right_fields, prefixed):
            if match is not None and field in match:
                out[name] = copy.deepcopy(match[field])
            else:
                out[name] = None
        result.append(out)
    return result
