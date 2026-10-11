"""Refresh the activity notebook in an existing JupyterLite output tree."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ROOT / "examples" / "stickyland-demo.ipynb",
    ROOT / "examples" / "stickyland-classroom.ipynb",
]
INDEX = ROOT / "_output" / "api" / "contents" / "all.json"

if not all(source.is_file() for source in SOURCES) or not INDEX.is_file():
    raise SystemExit("The source notebook or generated JupyterLite tree is missing")

index = json.loads(INDEX.read_text(encoding="utf-8"))
demo_entry = next(
    item for item in index["content"] if item.get("path") == "stickyland-demo.ipynb"
)

for source in SOURCES:
    target = ROOT / "_output" / "files" / source.name
    shutil.copy2(source, target)
    entry = next(
        (item for item in index["content"] if item.get("path") == source.name),
        None,
    )
    if entry is None:
        entry = dict(demo_entry)
        entry["name"] = source.name
        entry["path"] = source.name
        index["content"].append(entry)

    modified = datetime.fromtimestamp(target.stat().st_mtime, tz=timezone.utc)
    entry["size"] = target.stat().st_size
    entry["last_modified"] = modified.isoformat().replace("+00:00", "Z")
    print(f"Refreshed {target.relative_to(ROOT)} ({entry['size']:,} bytes)")

index["content"].sort(key=lambda item: item["path"])
INDEX.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
