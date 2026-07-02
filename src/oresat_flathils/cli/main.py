"""OreSat FlatHILS CLI Module."""

import sys

import click

from oresat_flathils.core.sim_only_runner import run_sim_only
from oresat_flathils.core.test_runner import run_pytest


@click.group()
def base() -> None:
    # ruff: disable[D205, D212, D400, D415]
    """
    ░█▀▀░█░░░█▀█░▀█▀░█░█░▀█▀░█░░░█▀▀░░░█▀▀░█░░░▀█▀
    ░█▀▀░█░░░█▀█░░█░░█▀█░░█░░█░░░▀▀█░░░█░░░█░░░░█░
    ░▀░░░▀▀▀░▀░▀░░▀░░▀░▀░▀▀▀░▀▀▀░▀▀▀░░░▀▀▀░▀▀▀░▀▀▀
    """
    # ruff: enable[D205, D212, D400, D415]


@click.command()
@click.argument("harness")
@click.option("--pytest_args", default="", help="Arguments to pass through to PyTest.")
def test(harness: str, pytest_args: str) -> None:
    """Run pytest with FlatHILS environment setup for a given harness."""
    try:
        run_pytest(pytest_args=[pytest_args], harness=harness)
    except (LookupError, ValueError) as exception:
        sys.stderr.write(f"flathils test: {exception}\n")


@click.command()
def sim_only() -> None:
    """Test building a simulation."""
    try:
        run_sim_only()
    except (LookupError, ValueError) as exception:
        sys.stderr.write(f"flathils test: {exception}\n")


# Register commands to main group.
base.add_command(test)
base.add_command(sim_only)
