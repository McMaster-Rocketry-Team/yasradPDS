"""Runs `yasradPDS analysis descent` on system.json and site.json and checks it exits cleanly.

Run with: .venv/Scripts/python tests/test_descent.py (replace slash with backslash)
"""
import json
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # no window, so plt.show() returns instead of blocking the test

from click.testing import CliRunner

from yasradPDS.interface.cli import cli

ROOT = Path(__file__).parents[1] / "src/yasradPDS/config"


def test_descent_exits_successfully():
    site = json.loads((ROOT / "site.json").read_text()) | {"atmosphere": "standard"}  # forecast needs NOAA up, too flaky for CI
    with tempfile.TemporaryDirectory() as tmp:
        site_path = Path(tmp) / "site.json"
        site_path.write_text(json.dumps(site))
        result = CliRunner().invoke(cli, ["analysis", "descent", "-i", str(ROOT / "system.json"), "-s", str(site_path)])
    assert result.exit_code == 0, f"{result.output}\n{result.exception!r}"


if __name__ == "__main__":
    test_descent_exits_successfully()
    print("ok")
