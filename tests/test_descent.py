"""Runs `yasradPDS analysis descent` on system.json and site.json and checks it exits cleanly.

Run with: .venv/Scripts/python tests/test_descent.py (replace slash with backslash)
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # no window, so plt.show() returns instead of blocking the test

from click.testing import CliRunner

from yasradPDS.interface.cli import cli

ROOT = Path(__file__).parents[1]


def test_descent_exits_successfully():
    result = CliRunner().invoke(cli, ["analysis", "descent", "-i", str(ROOT / "system.json"), "-s", str(ROOT / "site.json")])
    assert result.exit_code == 0, f"{result.output}\n{result.exception!r}"


if __name__ == "__main__":
    test_descent_exits_successfully()
    print("ok")
