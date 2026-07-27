"""OreSat FlatHILS CLI Module."""

import sys

import click

from oresat_flathils.core.runner import run_pytest


@click.group()
def base() -> None:
    """# noqa: D205, D212, D400, D415
    ░█▀▀░█░░░█▀█░▀█▀░█░█░▀█▀░█░░░█▀▀░░░█▀▀░█░░░▀█▀
    ░█▀▀░█░░░█▀█░░█░░█▀█░░█░░█░░░▀▀█░░░█░░░█░░░░█░
    ░▀░░░▀▀▀░▀░▀░░▀░░▀░▀░▀▀▀░▀▀▀░▀▀▀░░░▀▀▀░▀▀▀░▀▀▀
    """


@click.command()
@click.argument("harness")
@click.option("--run-hil", is_flag=True, default=False, help="Run hardware-in-the-loop tests.")
@click.option("--pytest-args", default="", help="Arguments to pass through to PyTest.")
def test(harness: str, run_hil: str, pytest_args: str) -> None:
    """Run pytest with FlatHILS environment setup for a given harness."""
    try:
        run_pytest(harness=harness, run_hil=run_hil, pytest_args=[pytest_args])
    except (LookupError, ValueError) as exception:
        sys.stderr.write(f"flathils test: {exception}\n")


# Register commands to main group.
base.add_command(test)
