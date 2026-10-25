def normalize_path(value):
    if not isinstance(value, str) or not value or not value.startswith('/'):
        raise ValueError('path must be a non-empty str starting with /')
    if '\x00' in value:
        raise ValueError('path must not contain NUL')
    segments = []
    for segment in value.split('/'):
        if not segment or segment == '.':
            continue
        if segment == '..':
            if not segments:
                raise ValueError('path escapes above root')
            segments.pop()
            continue
        segments.append(segment)
    return '/' + '/'.join(segments)
