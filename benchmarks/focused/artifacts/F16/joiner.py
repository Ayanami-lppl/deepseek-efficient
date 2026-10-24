import copy


def _is_name(value):
    return isinstance(value, str) and value != ""


def _validate_rows(rows, key, side):
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("%s row must be a dict" % side)
        for name in row:
            if not _is_name(name):
                raise ValueError("%s row field names must be non-empty str" % side)
        if key not in row:
            raise ValueError("%s row missing key %r" % (side, key))
        if not _is_name(row[key]):
            raise ValueError("%s join value must be a non-empty str" % side)


def left_join(left, right, key):
    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError("left and right must be lists of dicts")
    if not _is_name(key):
        raise ValueError("key must be a non-empty str")

    _validate_rows(left, key, "left")
    _validate_rows(right, key, "right")

    index = {}
    for row in right:
        value = row[key]
        if value in index:
            raise ValueError("duplicate right join value %r" % (value,))
        index[value] = row

    columns = sorted({name for row in right for name in row if name != key})
    prefixed = ["right." + name for name in columns]
    for row in left:
        for name in prefixed:
            if name in row:
                raise ValueError("left row already has output column %r" % (name,))

    result = []
    for row in left:
        match = index.get(row[key])
        out = {name: copy.deepcopy(value) for name, value in row.items()}
        for name, out_name in zip(columns, prefixed):
            out[out_name] = copy.deepcopy(match[name]) if match is not None and name in match else None
        result.append(out)
    return result
