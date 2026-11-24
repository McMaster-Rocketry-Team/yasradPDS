"""Runs `yasradPDS solve` on system.json and checks the system builds.

Run with: .venv/Scripts/python tests/test_create_system.py (replace slash with backslash)
"""
import json
import tempfile
from pathlib import Path

from click.testing import CliRunner

from yasradPDS.interface.cli import cli

SAMPLE = Path(__file__).parents[1] / "src/yasradPDS/config/system.json"


def run_create_system(inputs: dict | str):
    """Inputs as a dict, or raw file text to test unreadable files."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "system.json"
        path.write_text(inputs if isinstance(inputs, str) else json.dumps(inputs))
        return CliRunner().invoke(cli, ["solve", "-i", str(path), "--show"])


def sample() -> dict:
    return json.loads(SAMPLE.read_text())


def assert_clean_error(result, message: str):
    """Exit code 1 with a one-line 'Error: ...', not a traceback."""
    assert isinstance(result.exception, SystemExit), f"crashed: {result.exception!r}"
    assert result.exit_code == 1, result.output
    assert f"Error: {message}" in result.output, result.output


def test_sample_builds():
    inputs = sample()
    result = run_create_system(inputs)
    print(result.output)
    assert result.exit_code == 0, result.output
    assert f"Created system {inputs['name']!r} with 2 stages" in result.output
    assert "[drogue]" in result.output and "[main]" in result.output


def test_bad_inputs_give_clean_error():
    inputs = sample()
    inputs["main"]["mass_upper"] += 1  # total mass no longer matches the drogue
    assert_clean_error(run_create_system(inputs), "total mass differs")


def test_missing_default_file():
    with tempfile.TemporaryDirectory() as tmp:
        result = CliRunner().invoke(cli, ["solve", "-i", str(Path(tmp) / "system.json")])
    assert result.exit_code == 2, result.output  # click's usage error
    assert "does not exist" in result.output


def test_broken_json():
    assert_clean_error(run_create_system("{not json"), "")
    assert "is not valid JSON" in run_create_system("{not json").output


def test_missing_line():
    inputs = sample()
    del inputs["main"]["shroud"]
    assert_clean_error(run_create_system(inputs), "")
    assert "shroud" in run_create_system(inputs).output


def test_negative_mass():
    inputs = sample()
    inputs["main"]["mass_upper"] = -1.0
    assert_clean_error(run_create_system(inputs), "main: mass_upper must be >= 0")


def test_zero_break_strength():
    inputs = sample()
    inputs["main"]["shroud"]["break_strength"] = 0.0
    assert_clean_error(run_create_system(inputs), "main.shroud: _Line.break_strength must be > 0")


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
    print("all passed")
