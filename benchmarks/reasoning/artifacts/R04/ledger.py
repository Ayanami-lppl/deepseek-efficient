_FIELDS = frozenset(('id', 'src', 'dst', 'cents'))


def _is_name(value):
    return isinstance(value, str) and value != ''


def _is_cents(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _validate_balances(balances):
    if not isinstance(balances, dict):
        raise ValueError('balances must be a dict')
    for name, amount in balances.items():
        if not _is_name(name):
            raise ValueError('account name must be a non-empty string')
        if (not isinstance(amount, int) or isinstance(amount, bool)
                or amount < 0):
            raise ValueError('balance must be a non-negative int')


def move_money(balances, transfers):
    _validate_balances(balances)
    if not isinstance(transfers, list):
        raise ValueError('transfers must be a list')

    result = dict(balances)
    seen = {}
    for event in transfers:
        if not isinstance(event, dict) or set(event) != _FIELDS:
            raise ValueError('event must have exactly id/src/dst/cents')
        ident = event['id']
        src = event['src']
        dst = event['dst']
        cents = event['cents']
        if not (_is_name(ident) and _is_name(src) and _is_name(dst)
                and _is_cents(cents)):
            raise ValueError('invalid event fields')

        content = (src, dst, cents)
        if ident in seen:
            if seen[ident] != content:
                raise ValueError('conflicting duplicate event id')
            continue
        seen[ident] = content

        if src not in result or dst not in result:
            raise ValueError('unknown account')
        if result[src] < cents:
            raise ValueError('insufficient funds')
        if src != dst:
            result[src] -= cents
            result[dst] += cents
    return result
