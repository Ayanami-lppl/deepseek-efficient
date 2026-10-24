import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

RULES_FILE = Path(__file__).with_name("rules.json")


def _load_rate():
    try:
        data = json.loads(RULES_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("rules.json is unreadable or invalid JSON") from exc
    if not isinstance(data, dict) or "rate" not in data:
        raise ValueError("rules.json has no rate field")
    raw = data["rate"]
    if isinstance(raw, bool) or not isinstance(raw, (str, int, float)):
        raise ValueError("rate is not a decimal number")
    try:
        rate = Decimal(str(raw))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("rate is not a decimal number") from exc
    if not rate.is_finite() or not (Decimal(0) <= rate <= Decimal(1)):
        raise ValueError("rate must be a finite decimal between 0 and 1")
    return rate


def calc_total(cents):
    if isinstance(cents, bool) or not isinstance(cents, int) or cents < 0:
        raise ValueError("cents must be a non-negative integer")
    rate = _load_rate()
    total = Decimal(cents) * (Decimal(1) + rate)
    return int(total.quantize(Decimal(1), rounding=ROUND_HALF_UP))
