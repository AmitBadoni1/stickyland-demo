"""Refresh the activity notebook in an existing JupyterLite output tree."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "examples" / "stickyland-demo.ipynb"
TARGET = ROOT / "_output" / "files" / SOURCE.name
INDEX = ROOT / "_output" / "api" / "contents" / "all.json"

if not SOURCE.is_file() or not TARGET.parent.is_dir() or not INDEX.is_file():
    raise SystemExit("The source notebook or generated JupyterLite tree is missing")

shutil.copy2(SOURCE, TARGET)
index = json.loads(INDEX.read_text(encoding="utf-8"))
entry = next(
    (item for item in index["content"] if item.get("path") == SOURCE.name),
    None,
)
if entry is None:
    raise SystemExit(f"{SOURCE.name} is not indexed by the generated site")

modified = datetime.fromtimestamp(TARGET.stat().st_mtime, tz=timezone.utc)
entry["size"] = TARGET.stat().st_size
entry["last_modified"] = modified.isoformat().replace("+00:00", "Z")
INDEX.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
print(f"Refreshed {TARGET.relative_to(ROOT)} ({entry['size']:,} bytes)")
