# handles commands, routes inputs
"""
Instead of argparse, using click library
https://click.palletsprojects.com/en/stable/#documentation

Why click?
It's a lot easier to read compared to argparse and can easily add more cli commands.

climage for yasradPDS iamge
"""

"""
TODO:
- Fill the dropdown from _MODELS. Using sorted(atm._MODELS) for the choices keeps the GUI in step if you add a model later. If you'd rather not reach into a private name from the GUI, drop the leading underscore and call it MODELS.
- Convert GUI text before calling build(). Text fields give you strings, so convert them first:
  - for forecast, turn the date into a datetime
  - for custom, turn the wind into a float, or into a list of (height ASL, m/s) pairs for a profile
- Show only the fields for the chosen model. standard needs only the site. custom needs the two wind values. forecast needs a date, and the source is optional. Anything extra gets passed to the model's function, which will raise a TypeError.
- Heights in a wind profile are above sea level, not above the launch pad. Either label the field clearly or let users enter heights above ground and run them through atm.asl() before calling build().
"""

import click 
#import climage

@click.version_option(package_name="yasradPDS", prog_name="yasradPDS")
@click.group()
def cli():
    # SRAD Parachute Design System
    pass

DEFAULT_CONFIG = "system.json"

@cli.command()
def config():
    from yasradPDS.interface.dual_deploy_gui import prompt_inputs
    # the GUI's Save button picks the file and writes it
    if prompt_inputs() is None:
        click.echo("No changes made.")
        return
    click.echo("Inputs saved.")

@cli.command("create-system")
@click.option("-i", "path", default = DEFAULT_CONFIG, show_default = True, type = click.Path(exists = True, dir_okay = False), help = "Inputs saved by config")
@click.option("--show", is_flag = True, help = "Print every stage's values after building.")
def create_system(path, show):
    import json
    from yasradPDS.systems.system import new_system
    with open(path) as f:
        inputs = json.load(f)
    name = inputs.pop("name", "") # System doesn't take name so remove it from the json
    try:
        system = new_system("dual_deploy", **inputs)
    except (TypeError, ValueError) as e:
        raise click.ClickException(str(e))
    click.echo(f"Created system {name!r} with {system.stage_count} stages")
    if show:
        click.echo(system)

@cli.command()
@click.option("--preview", is_flag = True, help = "Matplotlib preview.")
def analyze(preview):
    # Run design analysis
    click.echo("implement analysis")
    # TODO: load system for analysis, get results

@cli.command()
@click.argument("format", type = click.Choice(["csv", "pdf", "dxf"]))
@click.option("-o", "path", required = True, type = click.Path(dir_okay = False), help = "Output file path")
def export(format, path):
    # Export design/results
    click.echo(f"Export {format} to {path}")
    # TODO: call export module