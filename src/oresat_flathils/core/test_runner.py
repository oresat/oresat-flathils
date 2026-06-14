"""OreSat FlatHILS Core Module Test Runner."""

import logging
import tomllib
from pathlib import Path
from typing import cast

import pytest

log = logging.getLogger("test_runner")


def run_pytest(pytest_args: list[str], harness: str | None = None) -> int:
    """Test runner entrypoint tries to load the appropriate harness configuration."""
    args = list(pytest_args)

    if harness:
        try:
            config = _get_harness_config(harness)
            test_dir = config.get("test_dir")

            if test_dir:
                args.append(test_dir)
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
