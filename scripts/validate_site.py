"""Fail the build if the generated JupyterLite site regresses to mixed stacks."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "_output"


def require(path: Path) -> Path:
    if not path.is_file():
        raise SystemExit(f"Missing generated file: {path.relative_to(ROOT)}")
    return path


require(OUTPUT / "index.html")
require(OUTPUT / "lab" / "index.html")
config = json.loads(require(OUTPUT / "jupyter-lite.json").read_text(encoding="utf-8"))
extensions = config["jupyter-config-data"]["federated_extensions"]
names = {extension["name"] for extension in extensions}

required = {"jupyterlab-stickyland", "@jupyterlite/pyodide-kernel-extension"}
missing = required - names
if missing:
    raise SystemExit(f"Missing required federated extensions: {sorted(missing)}")

for forbidden in ("@jupyter-notebook/lab-extension", "jupyterlab-plotly"):
    if forbidden in names:
        raise SystemExit(f"Incompatible optional extension was bundled: {forbidden}")

sticky = next(extension for extension in extensions if extension["name"] == "jupyterlab-stickyland")
sticky_package = json.loads(
    require(OUTPUT / "extensions" / Path(sticky["name"]) / "package.json").read_text(
        encoding="utf-8"
    )
)
for dependency in ("@jupyterlab/application", "@jupyterlab/apputils", "@jupyterlab/notebook"):
    if sticky_package["dependencies"][dependency] != "3.5.3":
        raise SystemExit(f"Unexpected StickyLand dependency: {dependency}")

pyodide_schema = require(
    OUTPUT
    / "extensions"
    / "@jupyterlite"
    / "pyodide-kernel-extension"
    / "static"
    / "schema"
    / "kernel.v0.schema.json"
).read_text(encoding="utf-8")
if "v0.24.1" not in pyodide_schema:
    raise SystemExit("The generated site is not pinned to Pyodide 0.24.1")

piplite_index = json.loads(
    require(OUTPUT / "pypi" / "all.json").read_text(encoding="utf-8")
)
if set(piplite_index.get("ipython", {}).get("releases", {})) != {"8.16.1"}:
    raise SystemExit("The browser runtime is not pinned to IPython 8.16.1")
if set(piplite_index.get("matplotlib-inline", {}).get("releases", {})) != {
    "0.1.6"
}:
    raise SystemExit("The browser runtime is not pinned to matplotlib-inline 0.1.6")

activity_notebook = json.loads(
    require(OUTPUT / "files" / "stickyland-demo.ipynb").read_text(encoding="utf-8")
)
require(OUTPUT / "files" / "stickyland-classroom.ipynb")
require(OUTPUT / "files" / "stickyland-analysis.ipynb")
if len(activity_notebook.get("cells", [])) < 30:
    raise SystemExit("The classroom activity notebook is unexpectedly short")

activity_tags = {
    tag
    for cell in activity_notebook["cells"]
    for tag in cell.get("metadata", {}).get("tags", [])
}
for required_tag in ("scenario-control", "analysis-audit", "analysis-output"):
    if required_tag not in activity_tags:
        raise SystemExit(f"The analysis notebook is missing tag: {required_tag}")

notebook_text = json.dumps(activity_notebook).lower()
for forbidden_text in ("submit_answer", "pass\" if passed", "objective submission"):
    if forbidden_text in notebook_text:
        raise SystemExit(
            f"The analysis notebook still contains validation UI: {forbidden_text}"
        )

print("Generated site is internally consistent.")
