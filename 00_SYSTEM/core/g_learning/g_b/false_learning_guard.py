def false_learning_guard(patterns, evidence_count):
    if evidence_count < 5:
        return True
    if any(p["count"] < 2 for p in patterns):
        return True
    return False
