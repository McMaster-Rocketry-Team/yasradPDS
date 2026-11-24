"""Checks the GUI's per-stage validation (stage_error) without opening a window.

Run with: .venv/Scripts/python tests/test_stage_error.py (replace slash with backslash)
"""
import json
from pathlib import Path

from yasradPDS.interface.dual_deploy_gui import stage_error

SAMPLE = Path(__file__).parents[1] / "src/yasradPDS/config/system.json"


def stage(name: str) -> dict:
    return json.loads(SAMPLE.read_text())[name]


def error(s: dict) -> str:
    """The error stage_error gives, failing the test if it gives none."""
    message = stage_error(s)
    assert message is not None, f"expected an error for {s}"
    return message


def test_both_diameters_pass():
    assert stage_error(stage("drogue")) is None


def test_no_diameters_pass():
    assert stage_error(stage("main")) is None


def test_only_one_diameter_fails():
    s = stage("drogue")
    del s["spill_hole_diameter"]
    assert "Fill in both" in error(s)

    s = stage("main")
    s["main_diameter"] = 2.0
    assert "Fill in both" in error(s)


def test_inf_fails():
    s = stage("main")
    s["deploy_velocity"] = float("inf")
    assert "inf" in error(s)

    s = stage("main")
    s["shroud"]["density"] = float("inf")  # inside a line, too
    assert "inf" in error(s)


def test_max_epsilon_range():
    for bad in (0.0, -0.1, 1.5):
        s = stage("main")
        s["cord_upper"]["max_epsilon"] = bad
        assert "MAX EPSILON" in error(s), bad

    s = stage("main")
    s["cord_upper"]["max_epsilon"] = 1.0  # upper bound is allowed
    assert stage_error(s) is None


if __name__ == "__main__":
    for name, test in list(globals().items()):
        if name.startswith("test_"):
            test()
    print("all passed")
