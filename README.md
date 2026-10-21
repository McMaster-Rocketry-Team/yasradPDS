# yasradPDS

**SRAD Parachute Design System**: a simulation-based design tool for the
McMaster Rocketry team's parachute recovery systems. Size a canopy,
get the gore pattern to cut, and see the loads, descent and landing
dispersion that go with it.

## How it works

Everything revolves around one **system object** (for example a
dual-deploy drogue + main system). It is the canonical data store: it
holds the knowns and unknowns, and it is passed to every analysis,
render and export so they all read the same data.

**Inputs.** Three knowns must be given:

- target apogee
- altitude of main deployment
- target descent rate (velocity)

**Computed values.** The unknowns the simulation needs (canopy and
shroud line dimensions, for example) are not entered by hand. They are
computed from the knowns when the system is created.

```
interface  ->  systems  ->  geometries
                  |
                  +-->  analysis   (descent, dispersion, stability)
                  +-->  render     (graphs, previews, maps)
                  +-->  export     (CSV, DXF, PDF, report)
```

Geometry objects are only imported by system files, so the shared code
works the same no matter which canopy shape is used.

## Setup

Requires Python 3.

```shell
python -m venv .venv
.venv\Scripts\activate          # Windows PowerShell
pip install -r requirements.txt
```

## Usage

```shell
python -m yasradPDS.main config      # open the popup to enter design values
python -m yasradPDS.main run         # size the system and run the analyses
python -m yasradPDS.main export      # write gore pattern, data and report
```

`config` opens a small entry window that closes when you update it.
Matplotlib previews and analysis results open as separate popups.
Exports are triggered from the CLI.

## Project layout

Code is under `src/yasradPDS/`.

| Folder | What it holds |
| --- | --- |
| `utils/` | Constants, unit conversion, atmosphere model, physics (all physics lives here) |
| `config/` | Default values (`defaults.json`) and the code that loads them |
| `geometries/` | Canopy shape interface (`Geometry` protocol) and each shape, e.g. semi-hemispherical |
| `systems/` | System interface and the dual-deploy drogue + main system |
| `analysis/` | RocketPy-assisted descent and opening shock, Monte Carlo dispersion, shroud line stability |
| `render/` | Time graphs, gore preview, 3D preview, dispersion map |
| `export/` | CSV data, DXF and PDF gore templates, text report, file saving |
| `interface/` | CLI command routing and the dual-deploy input GUI |

`main.py` is the entry point that starts the interface.

## Credits/Sources

- [RocketPy Library](https://rocketpy-team.github.io/)
