import csv
import io
from decimal import Decimal, InvalidOperation

HEADER = ["customer", "amount"]


def aggregate(text):
    """Aggregate CSV rows into {customer: total Decimal} in first-seen order."""
    if not isinstance(text, str):
        raise ValueError("text must be a string")
    text = text.lstrip("\ufeff")
    reader = csv.reader(io.StringIO(text, newline=""))
    rows = iter(reader)

    header = next(rows, None)
    if header is None:
        return {}
    if [cell.strip() for cell in header] != HEADER:
        raise ValueError("header must be: customer,amount")

    result = {}
    for row in rows:
        if not row or (len(row) == 1 and not row[0].strip()):
            continue
        if len(row) != 2:
            raise ValueError("each data row must have exactly 2 fields")
        name = row[0].strip()
        amount_text = row[1].strip()
        if not name:
            raise ValueError("customer name must not be empty")
        try:
            amount = Decimal(amount_text)
        except (InvalidOperation, ValueError):
            raise ValueError("amount must be a finite decimal number")
        if not amount.is_finite():
            raise ValueError("amount must be a finite decimal number")
        result[name] = result.get(name, Decimal(0)) + amount
    return result
