"""The HTML/CSS/JS port in web/ must reproduce the Python implementation exactly.

Exports reference outputs with web/tools/export_parity.py, then runs the Node parity tests
(web/tests/parity.test.mjs). Skipped when Node.js is not installed. No network.
"""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")


@pytest.mark.skipif(NODE is None, reason="Node.js is not installed")
def test_javascript_port_matches_python(tmp_path: Path) -> None:
    spec = importlib.util.spec_from_file_location(
        "export_parity", ROOT / "web" / "tools" / "export_parity.py"
    )
    exporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exporter)
    reference = tmp_path / "parity.json"
    exporter.main(reference)

    run = subprocess.run(
        [NODE, "--test", str(ROOT / "web" / "tests" / "parity.test.mjs")],
        env={**os.environ, "PARITY_JSON": str(reference)},
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert run.returncode == 0, run.stdout[-4000:] + run.stderr[-2000:]
