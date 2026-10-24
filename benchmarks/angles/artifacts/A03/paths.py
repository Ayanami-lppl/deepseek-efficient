def normalize_path(value):
    if not isinstance(value, str) or not value.startswith('/') or '\x00' in value:
        raise ValueError('invalid path')
    stack = []
    for segment in value.split('/'):
        if segment in ('', '.'):
            continue
        if segment == '..':
            if not stack:
                raise ValueError('path escapes root')
            stack.pop()
        else:
            stack.append(segment)
    return '/' + '/'.join(stack)
