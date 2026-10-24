def merge_intervals(intervals):
    ordered = []
    for interval in intervals:
        start, end = interval
        if start > end:
            raise ValueError("start must not be greater than end")
        if start == end:
            continue
        ordered.append((start, end))

    ordered.sort()
    merged = []
    for start, end in ordered:
        if merged and start < merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged
