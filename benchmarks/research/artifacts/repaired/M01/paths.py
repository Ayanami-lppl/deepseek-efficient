def normalize_path(value):
    if not isinstance(value, str) or not value or not value.startswith('/') or '\x00' in value:
        raise ValueError('path must be a non-empty string starting with "/" and contain no NUL')
    segments = []
    for segment in value.split('/'):
        if segment == '' or segment == '.':
            continue
        if segment == '..':
            if not segments:
                raise ValueError('path escapes root')
            segments.pop()
        else:
            segments.append(segment)
    return '/' + '/'.join(segments)
