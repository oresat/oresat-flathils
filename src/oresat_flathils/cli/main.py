"""OreSat FlatHILS CLI Module."""

import shlex
import subprocess
import sys

import click

from oresat_flathils.core.runner import run_pytest

from .harnesses import discover_harnesses, harness_dir


@click.group()
def base() -> None:
    """
    ░█▀▀░█░░░█▀█░▀█▀░█░█░▀█▀░█░░░█▀▀░░░█▀▀░█░░░▀█▀
    ░█▀▀░█░░░█▀█░░█░░█▀█░░█░░█░░░▀▀█░░░█░░░█░░░░█░
    ░▀░░░▀▀▀░▀░▀░░▀░░▀░▀░▀▀▀░▀▀▀░▀▀▀░░░▀▀▀░▀▀▀░▀▀▀
    """  # noqa: D205, D400, D415, D212


@base.group("list")
def list_group() -> None:
    """List available flathils resources."""


@list_group.command("harnesses")
def list_harnesses() -> None:
    """List all available test harnesses."""
    harnesses = discover_harnesses()
    if not harnesses:
        click.echo("No harnesses registered in pyproject.toml.")
        return
    for name in harnesses:
        click.echo(name)


def _complete_harness(_ctx: click.Context, _param: click.Parameter, incomplete: str) -> list[str]:
    return [h for h in discover_harnesses() if h.startswith(incomplete)]


@base.command("list-args")
@click.argument("harness", shell_complete=_complete_harness)
@click.pass_context
def list_args(ctx: click.Context, harness: str) -> None:
    """Show pytest options for a specific harness."""
    harnesses = discover_harnesses()
    if harness not in harnesses:
        click.echo(f"Error: unknown harness '{harness}'.\n", err=True)
        click.echo("Available harnesses:", err=True)
        for name in harnesses:
            click.echo(f"  {name}", err=True)
        ctx.exit(1)
    _show_harness_help(harness, ctx)


def _show_harness_help(harness: str, ctx: click.Context) -> None:
    """Get all options from conftest.py on each harness."""
    target_dir = harness_dir(harness)
    if not target_dir:
        click.echo(f"Harness '{harness}' has no directory configured in pyproject.toml.", err=True)
        ctx.exit(1)

    # target_dir is resolved via harness_dir(), which looks up a path from
    # pyproject.toml. It is not user-supplied directly. And no shell is involved either
    # (shell=False). Flagged by S603 only because args aren't string literals.
    try:
        result = subprocess.run(  # noqa: S603
            [sys.executable, "-m", "pytest", str(target_dir), "--help"],
            capture_output=True,
            text=True,
            check=False,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        click.echo(f"pytest timed out while inspecting harness '{harness}'.", err=True)
        ctx.exit(1)

    if result.returncode != 0:
        click.echo(f"pytest failed to inspect harness '{harness}':\n{result.stderr}", err=True)
        ctx.exit(1)

    section = _extract_custom_options(result.stdout)
    section = _format_custom_options(section) if section else section
    click.echo(f"Usage: flathils test {harness} [--run-hil] -- [PYTEST_ARGS]\n")
    click.echo(f"pytest options for harness '{harness}':\n")
    click.echo(section or "  (none registered)")


def _extract_custom_options(pytest_help_output: str) -> str:
    """Pull just the 'Custom options:' section out of pytest's own --help text."""
    lines = pytest_help_output.splitlines()
    start = next(
        (i for i, line in enumerate(lines) if line.strip().lower().startswith("custom options:")),
        None,
    )
    if start is None:
        return ""
    end = next(
        (
            i
            for i, line in enumerate(lines[start + 1 :], start + 1)
            if line and not line.startswith(" ")
        ),
        len(lines),
    )
    return "\n".join(lines[start:end])


def _format_custom_options(section: str) -> str:
    """Add a blank line between each option block for readability."""
    lines = section.splitlines()
    out: list[str] = [lines[0]] if lines else []  # "Custom options:" header

    for line in lines[1:]:
        is_new_option = line.startswith("  --")
        if is_new_option and out and out[-1].strip():
            out.append("")  # blank line before each new option
        out.append(line)

    return "\n".join(out)


@base.command("test")
@click.argument("harness")
@click.option("--run-hil", is_flag=True, default=False, help="Run hardware-in-the-loop tests.")
@click.option("--pytest-args", default="", help="Arguments to pass through to PyTest.")
def test(harness: str, run_hil: bool, pytest_args: str) -> None:  # noqa: FBT001
    """Run pytest with FlatHILS environment setup for a given harness."""
    if harness not in discover_harnesses():
        sys.stderr.write(
            f"flathils test: unknown harness '{harness}'. "
            f"Run 'flathils list harnesses' to see available harnesses.\n"
        )
        sys.exit(1)
    try:
        sys.exit(
            run_pytest(
                harness=harness,
                run_hil=run_hil,
                pytest_args=shlex.split(pytest_args),
            )
        )
    except (LookupError, ValueError) as exception:
        sys.stderr.write(f"flathils test: {exception}\n")
        sys.exit(1)
