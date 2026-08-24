"""OreSat FlatHILS CLI Module."""

import sys

import click
import pytest

from oresat_flathils.core.runner import run_pytest
from oresat_flathils.harness_args import HARNESSES


@click.group()
def base() -> None:
    """
    ░█▀▀░█░░░█▀█░▀█▀░█░█░▀█▀░█░░░█▀▀░░░█▀▀░█░░░▀█▀
    ░█▀▀░█░░░█▀█░░█░░█▀█░░█░░█░░░▀▀█░░░█░░░█░░░░█░
    ░▀░░░▀▀▀░▀░▀░░▀░░▀░▀░▀▀▀░▀▀▀░▀▀▀░░░▀▀▀░▀▀▀░▀▀▀
    """  # noqa: D205, D400, D415, D212


@click.command()
@click.argument("harness")
@click.option("--run-hil", is_flag=True, default=False, help="Run hardware-in-the-loop tests.")
@click.option("--pytest-args", default="", help="Arguments to pass through to PyTest.")
def test(harness: str, run_hil: bool, pytest_args: str) -> None:  # noqa: FBT001
    """Run pytest with FlatHILS environment setup for a given harness."""
    try:
        sys.exit(
            run_pytest(
                harness=harness,
                run_hil=run_hil,
                pytest_args=pytest_args.split(),
            )
        )
    except (LookupError, ValueError) as exception:
        sys.stderr.write(f"flathils test: {exception}\n")


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add Options from harness_args to click."""
    for add_fn in HARNESSES.values():
        add_fn(parser)


@click.command()
def harnesses() -> None:
    """List all FlatHILS harnesses and their arguments."""
    for name, add_fn in HARNESSES.items():
        parser = pytest.Parser()
        add_fn(parser)
        click.echo(f"{name}:")
        for opt in parser.anonymous.options:
            flag = opt.names()[-1]
            help_text = opt.attrs().get("help", "")
            default = opt.attrs().get("default")
            click.echo(f"  {flag:<20} {help_text}  (default: {default})")


# Register commands to main group.
base.add_command(test)
base.add_command(harnesses)
