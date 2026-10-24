import csv
import io
import re
from decimal import Decimal, InvalidOperation


_AMOUNT_RE = re.compile(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?")


def _exact_add(a, b):
    """Return a + b without rounding to the current decimal context."""
    if not a:
        return b
    if not b:
        return a

    ta = a.as_tuple()
    tb = b.as_tuple()
    exponent = min(ta.exponent, tb.exponent)

    def scaled(t):
        value = 0
        for digit in t.digits:
            value = value * 10 + digit
        value *= 10 ** (t.exponent - exponent)
        return -value if t.sign else value

    total = scaled(ta) + scaled(tb)
    sign = 1 if total < 0 else 0
    digits = tuple(int(ch) for ch in str(abs(total)))
    return Decimal((sign, digits, exponent))


def _is_blank(row):
    return not row or (len(row) == 1 and not row[0].strip())


def aggregate(text):
    if text.startswith("\ufeff"):
        text = text[1:]
    if not text.strip():
        return {}

    rows = [row for row in csv.reader(io.StringIO(text, newline="")) if not _is_blank(row)]
    if not rows:
        return {}

    if [cell.strip() for cell in rows[0]] != ["customer", "amount"]:
        raise ValueError("header must be 'customer,amount'")

    result = {}
    for row in rows[1:]:
        if len(row) != 2:
            raise ValueError("each row must have exactly 2 fields")

        name = row[0].strip()
        amount_text = row[1].strip()
        if not name:
            raise ValueError("customer name must not be empty")
        if not _AMOUNT_RE.fullmatch(amount_text):
            raise ValueError("invalid amount: %r" % (amount_text,))

        try:
            amount = Decimal(amount_text)
        except InvalidOperation:
            raise ValueError("invalid amount: %r" % (amount_text,))
        if not amount.is_finite():
            raise ValueError("invalid amount: %r" % (amount_text,))

        if name in result:
            result[name] = _exact_add(result[name], amount)
        else:
            result[name] = amount

    return result
