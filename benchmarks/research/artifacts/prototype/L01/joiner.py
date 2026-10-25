import copy


def _validate_rows(rows, side, key):
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(f'{side} row must be a dict')
        for name, value in row.items():
            if not isinstance(name, str) or not name:
                raise ValueError(f'{side} field names must be non-empty strings')
            try:
                copy.deepcopy(value)
            except Exception as exc:
                raise ValueError(f'{side} value for {name!r} is not deep-copyable') from exc
        if key not in row:
            raise ValueError(f'{side} row is missing key {key!r}')
        value = row[key]
        if not isinstance(value, str) or not value:
            raise ValueError(f'{side} key values must be non-empty strings')


def left_join(left, right, key):
    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError('left and right must be lists')
    if not isinstance(key, str) or not key:
        raise ValueError('key must be a non-empty string')

    _validate_rows(left, 'left', key)
    _validate_rows(right, 'right', key)

    columns = []
    seen = set()
    index = {}
    for row in right:
        value = row[key]
        if value in index:
            raise ValueError(f'duplicate right key {value!r}')
        index[value] = row
        for name in row:
            if name != key and name not in seen:
                seen.add(name)
                columns.append(name)

    prefixed = ['right.' + name for name in columns]
    for row in left:
        if any(name in row for name in prefixed):
            raise ValueError('left row already contains a generated column name')

    result = []
    for row in left:
        out = copy.deepcopy(row)
        match = index.get(row[key])
        for name, out_name in zip(columns, prefixed):
            out[out_name] = copy.deepcopy(match[name]) if match is not None and name in match else None
        result.append(out)
    return result
