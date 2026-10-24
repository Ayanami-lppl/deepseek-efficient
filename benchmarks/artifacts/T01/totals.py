"""Aggregate a ``customer,amount`` CSV into exact per-customer totals."""

import csv
import io
from decimal import Decimal, InvalidOperation


_HEADER = ("customer", "amount")


def aggregate(text):
    """Sum amounts per customer from CSV text.

    The first non-blank row must be the header ``customer,amount``.  Amounts
    are accumulated as :class:`~decimal.Decimal` values and the returned dict
    keeps customers in first-appearance order.  Malformed input raises
    :class:`ValueError`.
    """
    # Tolerate a UTF-8 BOM at the very beginning of the document.
    if text.startswith("\ufeff"):
        text = text[1:]

    result = {}
    header_seen = False

    for row in csv.reader(io.StringIO(text)):
        # Blank lines (including whitespace-only lines) carry no data.
        if not row or (len(row) == 1 and not row[0].strip()):
            continue

        if not header_seen:
            if [field.strip() for field in row] != list(_HEADER):
                raise ValueError("header must be 'customer,amount'")
            header_seen = True
            continue

        if len(row) != 2:
            raise ValueError("each data row must have exactly 2 fields")

        name = row[0].strip()
        raw_amount = row[1].strip()

        if not name:
            raise ValueError("customer name must not be empty")

        try:
            amount = Decimal(raw_amount)
        except (InvalidOperation, ValueError):
            raise ValueError(
                "amount is not a decimal number: {!r}".format(raw_amount)
            ) from None

        if not amount.is_finite():
            raise ValueError("amount is not finite: {!r}".format(raw_amount))

        result[name] = result.get(name, Decimal(0)) + amount

    return result
