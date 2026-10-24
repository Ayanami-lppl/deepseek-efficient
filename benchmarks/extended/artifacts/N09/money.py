import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from pathlib import Path


def _read_rate():
    path = Path(__file__).with_name("rules.json")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        raw_rate = data["rate"]
    except (OSError, UnicodeError, json.JSONDecodeError, TypeError, KeyError):
        raise ValueError("invalid rules.json") from None

    if isinstance(raw_rate, bool) or not isinstance(raw_rate, (str, int, float)):
        raise ValueError("invalid rate")

    try:
        rate = Decimal(str(raw_rate))
    except (InvalidOperation, ValueError):
        raise ValueError("invalid rate") from None

    if not rate.is_finite() or rate < 0 or rate > 1:
        raise ValueError("invalid rate")
    return rate


def calc_total(cents):
    if isinstance(cents, bool) or not isinstance(cents, int) or cents < 0:
        raise ValueError("cents must be a non-negative integer")

    rate = _read_rate()
    with localcontext() as ctx:
        ctx.prec = max(28, len(str(cents)) + len(rate.as_tuple().digits) + 30)
        total = Decimal(cents) * (Decimal(1) + rate)
        return int(total.to_integral_value(rounding=ROUND_HALF_UP))
