"""Runs `yasradPDS site` and checks the saved file loads back as a LaunchSite.

Run with: .venv/Scripts/python tests/test_site.py (replace slash with backslash)
"""
import json
import tempfile
from pathlib import Path

from click.testing import CliRunner

from yasradPDS.interface.cli import cli
from yasradPDS.utils.atmosphere import LaunchSite

ARGS = ["--name", "Launch Canada", "--latitude", "47.98", "--longitude", "-81.85", "--elevation", "390"]


def run_site(args):
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "site.json"
        result = CliRunner().invoke(cli, ["site", *args, "-o", str(path)])
        return result, (json.loads(path.read_text()) if path.exists() else None)


def test_site_round_trips():
    result, saved = run_site(ARGS)
    assert result.exit_code == 0, result.output
    assert LaunchSite.from_dict(saved) == LaunchSite("Launch Canada", 47.98, -81.85, 390.0)


def test_bad_site_not_saved():
    result, saved = run_site([*ARGS[:2], "--latitude", "100", *ARGS[4:]])
    assert result.exit_code == 1, result.output
    assert "latitude must be in [-90, 90]" in result.output
    assert saved is None


if __name__ == "__main__":
    test_site_round_trips()
    test_bad_site_not_saved()
    print("ok")
