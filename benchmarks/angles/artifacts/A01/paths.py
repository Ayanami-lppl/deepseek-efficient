def normalize_path(value):
    if not isinstance(value, str) or not value or not value.startswith('/') or '\0' in value:
        raise ValueError('path must be a non-empty absolute string without NUL characters')
    parts = []
    for segment in value.split('/'):
        if segment == '' or segment == '.':
            continue
        if segment == '..':
            if not parts:
                raise ValueError('path escapes above root')
            parts.pop()
        else:
            parts.append(segment)
    return '/' + '/'.join(parts)
