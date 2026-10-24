import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path


def _load_rate():
    path = Path(__file__).with_name("rules.json")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError) as exc:
        raise ValueError("invalid rules.json") from exc
    if not isinstance(data, dict) or "rate" not in data:
        raise ValueError("rules.json must contain a rate")
    value = data["rate"]
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise ValueError("rate must be a decimal number")
    try:
        rate = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("rate must be a decimal number") from exc
    if not rate.is_finite() or not Decimal(0) <= rate <= Decimal(1):
        raise ValueError("rate must be between 0 and 1")
    return rate


def calc_total(cents):
    if isinstance(cents, bool) or not isinstance(cents, int) or cents < 0:
        raise ValueError("cents must be a non-negative integer")
    rate = _load_rate()
    total = (Decimal(cents) * (Decimal(1) + rate)).to_integral_value(
        rounding=ROUND_HALF_UP
    )
    return int(total)
