def move_money(balances, transfers):
    if not isinstance(balances, dict):
        raise ValueError('balances must be a dict')

    result = {}
    for account, amount in balances.items():
        if not isinstance(account, str) or not account:
            raise ValueError('account names must be non-empty strings')
        if isinstance(amount, bool) or not isinstance(amount, int) or amount < 0:
            raise ValueError('balances must be non-negative ints')
        result[account] = amount

    if not isinstance(transfers, list):
        raise ValueError('transfers must be a list')

    fields = {'id', 'src', 'dst', 'cents'}
    seen = {}
    for transfer in transfers:
        if not isinstance(transfer, dict) or set(transfer) != fields:
            raise ValueError('each transfer must have exactly id/src/dst/cents')

        ident = transfer['id']
        src = transfer['src']
        dst = transfer['dst']
        cents = transfer['cents']
        if not isinstance(ident, str) or not ident:
            raise ValueError('id must be a non-empty string')
        if not isinstance(src, str) or not src:
            raise ValueError('src must be a non-empty string')
        if not isinstance(dst, str) or not dst:
            raise ValueError('dst must be a non-empty string')
        if not isinstance(cents, int) or isinstance(cents, bool) or cents <= 0:
            raise ValueError('cents must be a positive int')
        if src not in result or dst not in result:
            raise ValueError('src and dst must be existing accounts')

        signature = (src, dst, cents)
        if ident in seen:
            if seen[ident] != signature:
                raise ValueError('conflicting duplicate id')
            continue
        seen[ident] = signature

        if result[src] < cents:
            raise ValueError('insufficient funds')
        if src != dst:
            result[src] -= cents
            result[dst] += cents

    return result
