"""OreSat FlatHILS CLI Module."""

import click

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
@click.argument('harness')
def test(harness: str) -> None:
    """Run pytest with FlatHILS environment setup."""
    # FIXME: handle pytest_args
    # FIXME: Add exception handling
    run_pytest(pytest_args=[""], harness=harness)


# Register commands to main group.
base.add_command(test)
