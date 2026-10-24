import copy


def _validate(left, right, key):
    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError("left and right must be lists")
    if not isinstance(key, str) or not key:
        raise ValueError("key must be a non-empty string")

    def check_row(row, side):
        if not isinstance(row, dict):
            raise ValueError("%s row must be a dict" % side)
        for name, value in row.items():
            if not isinstance(name, str) or not name:
                raise ValueError("%s row has an invalid field name" % side)
        if key not in row:
            raise ValueError("%s row is missing the join key" % side)
        join_value = row[key]
        if not isinstance(join_value, str) or not join_value:
            raise ValueError("%s row has an invalid join value" % side)

    for row in left:
        check_row(row, "left")
    for row in right:
        check_row(row, "right")


def left_join(left, right, key):
    _validate(left, right, key)

    index = {}
    for row in right:
        join_value = row[key]
        if join_value in index:
            raise ValueError("duplicate right join value: %r" % (join_value,))
        index[join_value] = row

    right_fields = []
    seen = set()
    for row in right:
        for name in row:
            if name != key and name not in seen:
                seen.add(name)
                right_fields.append(name)

    generated = ["right." + name for name in right_fields]
    for row in left:
        for name in generated:
            if name in row:
                raise ValueError("left row already has column %r" % (name,))

    result = []
    for left_row in left:
        out = copy.deepcopy(left_row)
        matched = index.get(left_row[key])
        for name, out_name in zip(right_fields, generated):
            if matched is not None and name in matched:
                out[out_name] = copy.deepcopy(matched[name])
            else:
                out[out_name] = None
        result.append(out)
    return result
