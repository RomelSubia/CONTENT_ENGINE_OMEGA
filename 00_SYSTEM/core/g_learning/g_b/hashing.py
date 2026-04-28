import json, hashlib

def stable_hash(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
