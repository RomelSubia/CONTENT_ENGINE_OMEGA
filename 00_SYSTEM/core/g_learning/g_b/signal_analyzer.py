def analyze_signals(patterns, quality):
    signals = []
    for p in patterns:
        strength = min(1.0, p["count"]/5 * quality)
        level = "LOW"
        if strength > 0.7: level = "HIGH"
        elif strength > 0.4: level = "MEDIUM"

        signals.append({
            "pattern": p,
            "strength": strength,
            "level": level
        })
    return signals
