from .hashing import stable_hash
from .pattern_detector import detect_patterns
from .signal_analyzer import analyze_signals
from .false_learning_guard import false_learning_guard

def run_g_b(input_data):
    if input_data["status"] != "VALID":
        return {"status": "BLOCKED"}

    records = input_data["records"]
    quality = input_data["evidence_quality"]

    patterns = detect_patterns(records)

    if not patterns:
        return {"status": "NO_PATTERN_FOUND"}

    if false_learning_guard(patterns, input_data["evidence_count"]):
        return {"status": "REVIEW_REQUIRED"}

    signals = analyze_signals(patterns, quality)

    output = {
        "status": "VALID",
        "patterns": patterns,
        "signals": signals,
        "deterministic": True
    }

    output["output_hash"] = stable_hash(output)
    return output
