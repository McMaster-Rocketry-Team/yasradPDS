"""Checks the config's ft fields reach the system in m.

Run with: .venv/Scripts/python tests/test_units_in.py (replace slash with backslash)
"""
from yasradPDS.interface.cli import _to_meters


def test_ft_fields_become_meters():
    stage = {"deploy_altitude": 1000.0, "deploy_velocity": 30.0, "main_diameter": 10.0,
             "cord_upper": {"length": 20.0, "density": 0.01}}
    out = _to_meters({"name": "X", "main": stage})["main"]
    assert abs(out["deploy_altitude"] - 304.8) < 1e-9
    assert abs(out["main_diameter"] - 3.048) < 1e-9
    assert abs(out["cord_upper"]["length"] - 6.096) < 1e-9
    assert out["deploy_velocity"] == 30.0 and out["cord_upper"]["density"] == 0.01  # not plain lengths


if __name__ == "__main__":
    test_ft_fields_become_meters()
    print("ok")
