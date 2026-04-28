def detect_patterns(records):
    counts = {}
    for r in records:
        t = r["type"]
        counts[t] = counts.get(t, 0) + 1

    patterns = []
    for k,v in counts.items():
        if v >= 2:
            patterns.append({"type": k, "count": v})

    return patterns
