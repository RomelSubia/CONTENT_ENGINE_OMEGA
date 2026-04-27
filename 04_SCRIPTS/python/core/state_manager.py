from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


def read_json(path: Path | str) -> Any:
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json_atomic(path: Path | str, data: Any) -> None:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    payload = json.dumps(data, indent=2, ensure_ascii=True) + "\n"
    temp_path = file_path.with_name(file_path.name + ".tmp")

    with temp_path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())

    with temp_path.open("r", encoding="utf-8") as handle:
        temp_loaded = json.load(handle)

    os.replace(temp_path, file_path)

    with file_path.open("r", encoding="utf-8") as handle:
        replaced_loaded = json.load(handle)

    if replaced_loaded != temp_loaded or replaced_loaded != data:
        raise RuntimeError(f"Atomic write verification failed for {file_path}")
