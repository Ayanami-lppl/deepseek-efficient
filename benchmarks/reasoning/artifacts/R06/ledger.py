def _is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def move_money(balances, transfers):
    if not isinstance(balances, dict):
        raise ValueError('balances must be a dict')

    initial = {}
    for account, amount in balances.items():
        if not (isinstance(account, str) and account):
            raise ValueError('account names must be non-empty strings')
        if not (_is_int(amount) and amount >= 0):
            raise ValueError('balances must be non-negative ints')
        initial[account] = amount

    if not isinstance(transfers, list):
        raise ValueError('transfers must be a list')

    parsed = []
    for entry in transfers:
        if not isinstance(entry, dict) or set(entry) != {'id', 'src', 'dst', 'cents'}:
            raise ValueError('each transfer must have exactly id/src/dst/cents')
        ident, src, dst, cents = entry['id'], entry['src'], entry['dst'], entry['cents']
        if not (isinstance(ident, str) and ident):
            raise ValueError('id must be a non-empty string')
        if not (isinstance(src, str) and src) or not (isinstance(dst, str) and dst):
            raise ValueError('src and dst must be non-empty strings')
        if not (_is_int(cents) and cents > 0):
            raise ValueError('cents must be a positive int')
        if src not in initial or dst not in initial:
            raise ValueError('src and dst must be known accounts')
        parsed.append((ident, src, dst, cents))

    result = dict(initial)
    seen = {}
    for ident, src, dst, cents in parsed:
        if ident in seen:
            if seen[ident] != (src, dst, cents):
                raise ValueError('conflicting duplicate id')
            continue
        seen[ident] = (src, dst, cents)
        if result[src] < cents:
            raise ValueError('insufficient balance')
        if src != dst:
            result[src] -= cents
            result[dst] += cents
    return result
