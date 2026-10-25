def normalize_path(value):
    if not isinstance(value, str) or not value or not value.startswith('/') or '\x00' in value:
        raise ValueError('path must be a non-empty absolute string without NUL')
    parts = []
    for segment in value.split('/'):
        if segment in ('', '.'):
            continue
        if segment == '..':
            if not parts:
                raise ValueError('path escapes root')
            parts.pop()
        else:
            parts.append(segment)
    return '/' + '/'.join(parts)
