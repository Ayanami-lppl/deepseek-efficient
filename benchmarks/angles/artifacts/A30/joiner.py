import copy

_PREFIX = 'right.'


def _validate_rows(rows, key):
    if not isinstance(rows, list):
        raise ValueError('rows must be a list of dicts')
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('each row must be a dict')
        for name in row:
            if not isinstance(name, str) or not name:
                raise ValueError('field names must be non-empty str')
        if key not in row:
            raise ValueError('each row must contain the key field')
        if not isinstance(row[key], str) or not row[key]:
            raise ValueError('join values must be non-empty str')


def left_join(left, right, key):
    if not isinstance(key, str) or not key:
        raise ValueError('key must be a non-empty str')
    _validate_rows(left, key)
    _validate_rows(right, key)

    index = {}
    columns = []
    seen = set()
    for row in right:
        value = row[key]
        if value in index:
            raise ValueError('duplicate right join value')
        index[value] = row
        for name in row:
            if name != key and name not in seen:
                seen.add(name)
                columns.append(name)
    out_names = [_PREFIX + name for name in columns]

    for row in left:
        for name in out_names:
            if name in row:
                raise ValueError('prefix column collision: ' + name)

    result = []
    try:
        for row in left:
            out = copy.deepcopy(row)
            match = index.get(row[key])
            for name, out_name in zip(columns, out_names):
                if match is not None and name in match:
                    out[out_name] = copy.deepcopy(match[name])
                else:
                    out[out_name] = None
            result.append(out)
    except Exception as exc:
        raise ValueError('values must be deep-copyable') from exc
    return result
