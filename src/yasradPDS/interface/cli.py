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
  - for forecast/ensemble, turn the date into a datetime
  - for custom, turn the wind into a float, or into a list of (height ASL, m/s) pairs for a profile
- Show only the fields for the chosen model. standard needs only the site. custom needs the two wind values. forecast/ensemble need a date, and the source is optional. Anything extra gets passed to the model's function, which will raise a TypeError.
- Heights in a wind profile are above sea level, not above the launch pad. Either label the field clearly or let users enter heights above ground and run them through atm.asl() before calling build().
"""

import click 
#import climage

@click.version_option(package_name="yasradPDS", prog_name="yasradPDS")
@click.group()
def cli():
    # SRAD Parachute Design System
    pass

@cli.command()
def config():
    from yasradPDS.interface.dual_deploy_gui import prompt_inputs
    inputs = prompt_inputs()
    if inputs is None:
        click.echo("No changes made.")
        return
    click.echo(f"Got: {inputs}")
    # TODO: update and save design inputs into system object

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