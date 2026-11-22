# handles commands, routes inputs
"""
TODO: climage for yasradPDS image
"""

import click 
#import climage

@click.version_option(package_name="yasradPDS", prog_name="yasradPDS")
@click.group()
def cli():
    """SRAD Parachute Design System."""
    pass

DEFAULT_CONFIG = "system.json" # system inputs written by `config`, read by solve/analysis/export

# Dual deploy Config
@cli.command()
def config():
    """Open the dual deploy GUI to enter and save system inputs."""
    from yasradPDS.interface.dual_deploy_gui import prompt_inputs
    # the GUI's Save button picks the file and writes it
    if prompt_inputs() is None:
        click.echo("No changes made.")
        return
    click.echo("Inputs saved.")

DEFAULT_SITE = "site.json" # launch site written by `site`, read by analysis/export

# Shared loaders: turn bad files into a one-line click error instead of a traceback
def _load_json(path):
    import json
    with open(path) as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as e:
            raise click.ClickException(f"{path} is not valid JSON: {e}")

def _to_meters(values: dict) -> dict:
    """Config values with the GUI's ft fields converted to m, including inside line dicts."""
    from yasradPDS.interface.dual_deploy_gui import FT_FIELDS
    from yasradPDS.utils.units import convert_ft_m
    return {key: _to_meters(value) if isinstance(value, dict)
            else convert_ft_m(value, "m") if key in FT_FIELDS
            else value
            for key, value in values.items()}

def _load_system(path):
    """Returns (name, system) built from a config file (lengths in ft, see dual_deploy_gui.FT_FIELDS)."""
    from yasradPDS.systems.system import new_system
    inputs = _to_meters(_load_json(path)) # config is in ft, system calculates in m
    name = inputs.pop("name", "") # System doesn't take name so remove it from the json
    try:
        return name, new_system("dual_deploy", **inputs)
    except (TypeError, ValueError) as e:
        raise click.ClickException(str(e))

# Solves for System
@cli.command("solve")
@click.option("-i", "path", default = DEFAULT_CONFIG, show_default = True, type = click.Path(exists = True, dir_okay = False), help = "Inputs saved by config")
@click.option("--show", is_flag = True, help = "Print every stage's values after building.")
def create_system(path, show):
    """Build the system from the config file and check it solves."""
    name, system = _load_system(path)
    click.echo(f"Created system {name!r} with {system.stage_count} stages")
    if show:
        click.echo(system)

def _load_site(path):
    """Returns the LaunchSite saved by `site`."""
    from yasradPDS.utils.atmosphere import LaunchSite
    try:
        return LaunchSite.from_dict(_load_json(path))
    except Exception as e: # ValueError, TypeError, or pytz's UnknownTimeZoneError
        raise click.ClickException(f"{path}: {e}")

# Save a LaunchSite for analyses
@cli.command()
@click.option("--name", required = True)
@click.option("--latitude", required = True, type = float, help = "deg, + north")
@click.option("--longitude", required = True, type = float, help = "deg, + east")
@click.option("--elevation", required = True, type = float, help = "m ASL")
@click.option("--timezone", default = "UTC", show_default = True)
@click.option("-o", "path", default = DEFAULT_SITE, show_default = True, type = click.Path(dir_okay = False), help = "Where to save the site")
def site(name, latitude, longitude, elevation, timezone, path):
    """Save a launch site (location and ground elevation) for analysis and export."""
    import json
    from dataclasses import asdict
    from yasradPDS.utils.atmosphere import LaunchSite
    try:
        launch_site = LaunchSite(name, latitude, longitude, elevation, timezone) # validates lat/lon/elevation/timezone
    except Exception as e: # ValueError, or pytz's UnknownTimeZoneError
        raise click.ClickException(f"Invalid launch site: {e}")
    with open(path, "w") as f:
        json.dump(asdict(launch_site), f, indent = 2)
    click.echo(f"Saved launch site {name!r} to {path}")

# Run analyses (plots only; use `export` to save results)
@cli.command()
@click.argument("run_type", type = click.Choice(["descent", "montecarlo"]))
@click.option("-i", "path", default = DEFAULT_CONFIG, show_default = True, type = click.Path(exists = True, dir_okay = False), help = "Inputs saved by config")
@click.option("-s", "site_path", default = DEFAULT_SITE, show_default = True, type = click.Path(exists = True, dir_okay = False), help = "Launch site saved by site")
def analysis(run_type, path, site_path):
    """Run an analysis on the system at the launch site and plot the results."""
    from datetime import datetime
    _, system = _load_system(path)
    # date only matters for forecast weather; descent currently uses the standard atmosphere
    if run_type == "descent":
        from yasradPDS.analysis.descent import descent_analysis
        descent_analysis(system, _load_site(site_path), datetime.now())
    else:
        raise click.ClickException("montecarlo is not implemented yet")

# Export results to file
@cli.command()
@click.argument("format", type = click.Choice(["csv", "pdf", "dxf"]))
# need to add argument for what kind of analysis for each csv, pdf, dxf, etc.
@click.option("-o", "path", required = True, type = click.Path(dir_okay = False), help = "Output file path")
@click.option("-i", "system_path", default = DEFAULT_CONFIG, show_default = True, type = click.Path(exists = True, dir_okay = False), help = "Inputs saved by config")
@click.option("-s", "site_path", default = DEFAULT_SITE, show_default = True, type = click.Path(exists = True, dir_okay = False), help = "Launch site saved by site")

#TODO: must be able to select stage in cli for pdf/dxf export
def export(format, path, system_path, site_path):
    """Export results to a file. csv: descent altitude, velocity and acceleration vs time."""

    _, system = _load_system(system_path)

    if format == "csv": # shortcut: csv is descent data only; add an analysis-type argument when montecarlo exports exist
        from datetime import datetime
        from yasradPDS.analysis.descent import get_descent_flight_3_DOF
        from yasradPDS.export.csv_data import descent_csv
        # re-runs the descent without plotting; nothing is cached from `analysis`
        descent_csv(get_descent_flight_3_DOF(system, _load_site(site_path), datetime.now()), path)
        click.echo(f"Saved descent data to {path}")
    elif format == "dxf":
        from yasradPDS.export.dxf_template import export_dxf
        from yasradPDS.config.defaults import SEAM_ALLOWANCE as SA
        export_dxf(system.get(0, "gore_outline"), path, allowance_m = SA, preview = True)
    elif format == "pdf":
        from yasradPDS.export.pdf_template import pdf_export
        pdf_export(system, 0, path)
    else:
        click.echo(f"Unsupported file type.")
        # TODO: call export module