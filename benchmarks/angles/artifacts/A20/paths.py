def normalize_path(value):
    if not isinstance(value, str) or not value or not value.startswith('/') or '\0' in value:
        raise ValueError('path must be a non-empty absolute string without NUL')
    segments = []
    for segment in value.split('/'):
        if segment in ('', '.'):
            continue
        if segment == '..':
            if not segments:
                raise ValueError('path escapes root')
            segments.pop()
        else:
            segments.append(segment)
    return '/' + '/'.join(segments)
