"""Registry of specific pytest CLI options for each harness.

This is automatically in sync with pyproject.toml and fetches each harness.
if a harness is to have its own conftest, it will see each argument and fetch it.
"""

import tomllib
from pathlib import Path
from typing import cast

import click


def _find_pyproject(start: Path) -> Path | None:
    """Walk up from `start`("root") looking for a pyproject.toml."""
    for directory in (start, *start.parents):
        candidate = directory / "pyproject.toml"
        if candidate.is_file():
            return candidate
    return None


def _load_harness_config() -> dict[str, dict[str, str]]:
    """Load all availible harnesses, and what is needed."""
    pyproject_path = _find_pyproject(Path.cwd())
    if pyproject_path is None:
        click.echo(
            "flathils: could not find 'pyproject.toml' in the current directory "
            "or any parent directory. Run flathils from within the project.",
            err=True,
        )
        raise SystemExit(1)

    try:
        with pyproject_path.open("rb") as f:
            config = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        click.echo(f"flathils: failed to parse '{pyproject_path}': {exc}", err=True)
        raise SystemExit(1) from None

    harnesses = config.get("tool", {}).get("oresat_flathils", {}).get("harnesses", {})
    return cast("dict[str, dict[str, str]]", harnesses)


def discover_harnesses() -> list[str]:
    """List harness names as registered in pyproject.toml."""
    return sorted(_load_harness_config())


def harness_dir(harness: str) -> Path | None:
    """Look up a harness's directory from pyproject.toml, if registered."""
    pyproject_path = _find_pyproject(Path.cwd())
    if pyproject_path is None:
        return None
    rel = _load_harness_config().get(harness, {}).get("harness_dir")
    if rel is None:
        return None
    return pyproject_path.parent / rel
