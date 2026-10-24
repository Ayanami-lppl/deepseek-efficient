def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _check_balances(balances):
    if not isinstance(balances, dict):
        raise ValueError('balances must be a dict')
    for account, amount in balances.items():
        if not isinstance(account, str) or not account:
            raise ValueError('account name must be a non-empty string')
        if not _is_int(amount) or amount < 0:
            raise ValueError('balance must be a non-negative int')


def _check_event(event):
    if not isinstance(event, dict):
        raise ValueError('transfer must be a dict')
    if set(event) != {'id', 'src', 'dst', 'cents'}:
        raise ValueError('transfer must have exactly id/src/dst/cents')
    if not isinstance(event['id'], str) or not event['id']:
        raise ValueError('id must be a non-empty string')
    for field in ('src', 'dst'):
        if not isinstance(event[field], str) or not event[field]:
            raise ValueError('%s must be a non-empty string' % field)
    if not _is_int(event['cents']) or event['cents'] <= 0:
        raise ValueError('cents must be a positive int')


def move_money(balances, transfers):
    _check_balances(balances)
    if not isinstance(transfers, list):
        raise ValueError('transfers must be a list')

    result = dict(balances)
    seen = {}
    for event in transfers:
        _check_event(event)
        ident = event['id']
        content = (event['src'], event['dst'], event['cents'])
        if ident in seen:
            if seen[ident] != content:
                raise ValueError('conflicting duplicate id: %r' % (ident,))
            continue
        seen[ident] = content

        src, dst, cents = content
        if src not in result or dst not in result:
            raise ValueError('unknown account')
        if result[src] < cents:
            raise ValueError('insufficient funds')
        if src != dst:
            result[src] -= cents
            result[dst] += cents
    return result
