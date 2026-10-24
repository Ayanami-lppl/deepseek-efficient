def merge_intervals(intervals):
    """Merge overlapping half-open intervals without mutating the input.

    Intervals are ``(start, end)`` pairs with ``start < end``. Only genuine
    overlaps are merged; merely touching intervals stay separate. Zero-length
    intervals are ignored, and any ``start > end`` raises ``ValueError``.
    """
    checked = []
    for interval in intervals:
        start, end = interval
        if start > end:
            raise ValueError("invalid interval: start must not exceed end")
        if start == end:
            continue
        checked.append((start, end))

    checked.sort()

    merged = []
    for start, end in checked:
        if merged and start < merged[-1][1]:
            if end > merged[-1][1]:
                merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))

    return merged
