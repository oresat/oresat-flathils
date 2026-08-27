"""OreSat FlatHILS CLI Module."""

import sys

import click
import pytest

from oresat_flathils.core.runner import run_pytest
from oresat_flathils.harness_args import HARNESSES, REQUIRED_OPTIONS


@click.group()
def base() -> None:
    """
    ░█▀▀░█░░░█▀█░▀█▀░█░█░▀█▀░█░░░█▀▀░░░█▀▀░█░░░▀█▀
    ░█▀▀░█░░░█▀█░░█░░█▀█░░█░░█░░░▀▀█░░░█░░░█░░░░█░
    ░▀░░░▀▀▀░▀░▀░░▀░░▀░▀░▀▀▀░▀▀▀░▀▀▀░░░▀▀▀░▀▀▀░▀▀▀
    """  # noqa: D205, D400, D415, D212


def _check_required_options(harness: str, pytest_args: list[str]) -> None:
    """Validate that harness-specific required options were passed, if any are declared."""
    required = REQUIRED_OPTIONS.get(harness)
    if not required:
        return

    parser = pytest.Parser()
    for add_fn in HARNESSES.values():   # mirrors pytest_addoption: full merged parser
        add_fn(parser)
    namespace = parser.parse(pytest_args)

    missing = [
        f"--{dest.replace('_', '-')}"
        for dest in required
        if getattr(namespace, dest, None) in (None, False)
    ]
    if missing:
        raise ValueError(f"harness {harness!r} requires: {', '.join(missing)}")


@click.command()
@click.argument("harness")
@click.option("--run-hil", is_flag=True, default=False, help="Run hardware-in-the-loop tests.")
@click.option("--pytest-args", default="", help="Arguments to pass through to PyTest.")
def test(harness: str, run_hil: bool, pytest_args: str) -> None:  # noqa: FBT001
    """Run pytest with FlatHILS environment setup for a given harness."""
    try:
        args = pytest_args.split()
        _check_required_options(harness, args)
        sys.exit(run_pytest(harness=harness, run_hil=run_hil, pytest_args=args))
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
        for opt in parser._anonymous.options:  # noqa: SLF001
            # pytest.Parser has no public API for listing registered options
            flag = opt.names()[-1]
            help_text = opt.attrs().get("help", "")
            default = opt.attrs().get("default")
            click.echo(f"  {flag:<20} {help_text}  (default: {default})")


# Register commands to main group.
base.add_command(test)
base.add_command(harnesses)
