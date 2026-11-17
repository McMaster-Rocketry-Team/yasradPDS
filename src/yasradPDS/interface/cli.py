# handles commands, routes inputs
"""
Instead of argparse, using click library
https://click.palletsprojects.com/en/stable/#documentation

Why click?
It's a lot easier to read compared to argparse and can easily add more cli commands.

climage for yasradPDS iamge
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
        try:
            inputs = json.load(f)
        except json.JSONDecodeError as e:
            raise click.ClickException(f"{path} is not valid JSON: {e}")
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