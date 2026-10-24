def merge_intervals(intervals):
    cleaned = []
    for start, end in intervals:
        if start > end:
            raise ValueError("interval start must not be greater than end")
        if start == end:
            continue
        cleaned.append((start, end))

    cleaned.sort()
    merged = []
    for start, end in cleaned:
        if merged and start < merged[-1][1]:
            if end > merged[-1][1]:
                merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))
    return merged
