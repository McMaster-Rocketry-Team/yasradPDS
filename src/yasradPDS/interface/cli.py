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

@cli.command()
@click.option("--apogee", type = float, help = "Target apogee (m)")
@click.option("--main-alt", type = float, help = "Main deployment altitude (m)")
@click.option("--descent-rate", type = float, help = "Target descent rate (m/s)")
def config(apogee, main_alt, descent_rate):
    # Set design inputs
    click.echo(f"apogee={apogee}, main_alt={main_alt}, descent_rate={descent_rate}")
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