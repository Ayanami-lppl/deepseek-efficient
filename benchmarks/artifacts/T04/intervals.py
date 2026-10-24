def merge_intervals(intervals):
    """Merge overlapping half-open integer intervals.

    Intervals are ``(start, end)`` pairs covering ``start`` up to but not
    including ``end``.  The input may be unordered and may contain
    duplicates; it is never modified.  Zero-length intervals are ignored,
    and a ``ValueError`` is raised if any ``start`` is greater than its
    ``end``.

    Returns a list of ``(start, end)`` tuples sorted by start, where only
    genuinely overlapping intervals have been combined.  Adjacent
    intervals such as ``(1, 3)`` and ``(3, 5)`` are left separate.
    """
    normalized = []
    for interval in intervals:
        start, end = interval
        if start > end:
            raise ValueError(
                "interval start must not be greater than end: %r" % (interval,)
            )
        if start == end:
            continue
        normalized.append((start, end))

    normalized.sort(key=lambda item: (item[0], item[1]))

    merged = []
    for start, end in normalized:
        if merged and start < merged[-1][1]:
            if end > merged[-1][1]:
                merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))
    return merged
