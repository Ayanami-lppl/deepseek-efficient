from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import json
from pathlib import Path


def _load_rate():
    try:
        data = json.loads(Path(__file__).with_name("rules.json").read_text(encoding="utf-8"))
        value = data["rate"]
        if isinstance(value, bool):
            raise ValueError("invalid rate")
        rate = Decimal(str(value))
    except (OSError, json.JSONDecodeError, KeyError, TypeError, InvalidOperation) as exc:
        raise ValueError("invalid rules.json") from exc
    if not rate.is_finite() or not (0 <= rate <= 1):
        raise ValueError("rate must be a finite decimal between 0 and 1")
    return rate


def calc_total(cents):
    if isinstance(cents, bool) or not isinstance(cents, int) or cents < 0:
        raise ValueError("cents must be a non-negative integer")
    rate = _load_rate()
    total = Decimal(cents) * (Decimal(1) + rate)
    return int(total.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
