def normalize_path(value):
    if type(value) is not str or not value or not value.startswith('/'):
        raise ValueError('path must be a non-empty str starting with "/"')
    if '\x00' in value:
        raise ValueError('path must not contain NUL')

    parts = []
    for segment in value.split('/'):
        if segment == '' or segment == '.':
            continue
        if segment == '..':
            if not parts:
                raise ValueError('path escapes root')
            parts.pop()
        else:
            parts.append(segment)

    return '/' + '/'.join(parts)
