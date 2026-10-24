import json
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

RULES_PATH = Path(__file__).with_name("rules.json")


def _load_rate():
    try:
        rules = json.loads(RULES_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ValueError("invalid rules.json") from exc

    if not isinstance(rules, dict) or "rate" not in rules:
        raise ValueError("rules.json must contain rate")

    raw = rules["rate"]
    if isinstance(raw, bool) or raw is None:
        raise ValueError("rate must be a finite decimal number")

    try:
        rate = raw if isinstance(raw, Decimal) else Decimal(str(raw))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise ValueError("rate must be a finite decimal number") from exc

    if not rate.is_finite() or not (Decimal(0) <= rate <= Decimal(1)):
        raise ValueError("rate must be between 0 and 1")
    return rate


def calc_total(cents):
    if isinstance(cents, bool) or not isinstance(cents, int) or cents < 0:
        raise ValueError("cents must be a non-negative integer")

    rate = _load_rate()
    total = Decimal(cents) * (Decimal(1) + rate)
    return int(total.quantize(Decimal(1), rounding=ROUND_HALF_UP))
