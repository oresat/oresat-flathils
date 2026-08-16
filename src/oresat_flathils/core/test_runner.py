"""OreSat FlatHILS Core Module Test Runner."""

import logging
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING, cast

import pytest

if TYPE_CHECKING:
    import Iterable

log = logging.getLogger("test_runner")


def run_pytest(
    harness: str | None = None,
    run_hil: str | None = None,
    pytest_args: list[str] | Iterable[str] = None,
) -> int:
    """Test runner entrypoint tries to load the appropriate harness configuration."""
    args = list(pytest_args)
    args.append("--ignore=tests/")

    if run_hil:
        args.append("--run-hil")

    if harness:
        try:
            config = _get_harness_config(harness)
            harness_dir = config.get("harness_dir")

            if harness_dir:
                args.extend(["--lg-env", str(Path(harness_dir) / "env.yaml")])
                args.append(harness_dir)
        except Exception:
            log.exception("Error loading harness config")

            return 1

    return pytest.main(args)


def _get_harness_config(harness_name: str) -> dict[str, str]:
    """Fetch harness configuration from project config."""
    with Path("pyproject.toml").open("rb") as f:
        config = tomllib.load(f)

    harnesses = config.get("tool", {}).get("oresat_flathils", {}).get("harnesses", {})

    if harness_name not in harnesses:
        raise ValueError(f"Harness '{harness_name}' not found in pyproject.toml")

    return cast("dict[str, str]", harnesses[harness_name])
