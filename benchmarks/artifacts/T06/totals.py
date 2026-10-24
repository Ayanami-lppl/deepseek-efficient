import csv
import io
from decimal import Decimal, InvalidOperation, localcontext

HEADER = ["customer", "amount"]


def _parse_amount(raw):
    """Parse one amount field as a finite Decimal, else raise ValueError."""
    try:
        value = Decimal(raw)
    except (InvalidOperation, ValueError):
        raise ValueError("invalid amount: %r" % (raw,)) from None
    if not value.is_finite():
        raise ValueError("invalid amount: %r" % (raw,))
    return value


def aggregate(text):
    if text.startswith("\ufeff"):
        text = text[1:]

    rows = []
    for row in csv.reader(io.StringIO(text)):
        # csv.reader yields [] for empty lines and ['   '] for blank ones.
        if not row:
            continue
        if len(row) == 1 and not row[0].strip():
            continue
        rows.append(row)

    if not rows:
        return {}

    header = [cell.strip() for cell in rows[0]]
    if header != HEADER:
        raise ValueError("invalid header: %r" % (rows[0],))

    result = {}
    # Use a wide precision so sums of long decimals stay exact instead of
    # being rounded by the default 28-digit decimal context.
    with localcontext() as ctx:
        ctx.prec = 1000
        for row in rows[1:]:
            if len(row) != 2:
                raise ValueError("expected 2 fields, got %d: %r" % (len(row), row))
            name = row[0].strip()
            if not name:
                raise ValueError("empty customer name")
            amount = _parse_amount(row[1].strip())
            result[name] = result.get(name, Decimal(0)) + amount
    return result
