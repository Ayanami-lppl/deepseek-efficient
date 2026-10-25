def normalize_path(value):
    if type(value) is not str or not value or value[0] != '/' or '\x00' in value:
        raise ValueError('path must be a non-empty absolute path string')
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
