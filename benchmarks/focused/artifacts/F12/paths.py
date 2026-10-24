def normalize_path(value):
    if not isinstance(value, str):
        raise ValueError("path must be a str")
    if not value or not value.startswith('/') or '\x00' in value:
        raise ValueError("path must be non-empty, absolute, and NUL-free")
    segments = []
    for segment in value.split('/'):
        if segment in ('', '.'):
            continue
        if segment == '..':
            if not segments:
                raise ValueError("path escapes above root")
            segments.pop()
        else:
            segments.append(segment)
    return '/' + '/'.join(segments)
