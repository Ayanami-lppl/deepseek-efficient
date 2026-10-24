import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP, localcontext
from pathlib import Path

RULES_PATH = Path(__file__).with_name("rules.json")


def _load_rate():
    try:
        data = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("cannot read a valid rules.json") from exc

    if not isinstance(data, dict) or "rate" not in data:
        raise ValueError("rules.json must be an object containing 'rate'")

    raw = data["rate"]
    if isinstance(raw, bool) or not isinstance(raw, (str, int, float)):
        raise ValueError("rate must be a decimal number")

    try:
        rate = Decimal(raw) if isinstance(raw, int) else Decimal(str(raw))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("rate must be a decimal number") from exc

    if not rate.is_finite() or rate < 0 or rate > 1:
        raise ValueError("rate must be a finite decimal between 0 and 1")
    return rate


def calc_total(cents):
    if isinstance(cents, bool) or not isinstance(cents, int) or cents < 0:
        raise ValueError("cents must be a non-negative integer")

    rate = _load_rate()

    with localcontext() as ctx:
        ctx.prec = max(28, len(str(cents)) + 40)
        total = (Decimal(cents) * (Decimal(1) + rate)).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
    return int(total)
