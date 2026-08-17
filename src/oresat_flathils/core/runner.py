"""OreSat FlatHILS Core Module Test Runner."""

import logging
from typing import TYPE_CHECKING

import pytest

from oresat_flathils.cli.harnesses import harness_dir

if TYPE_CHECKING:
    from collections.abc import Iterable

log = logging.getLogger("runner")


def run_pytest(harness: str, run_hil: bool, pytest_args: Iterable[str]) -> int:  # noqa: FBT001
    """Test runner entrypoint tries to load the appropriate harness configuration."""
    args = list(pytest_args)
    args.append("--ignore=tests/")

    if run_hil:
        args.append("--run-hil")

    if harness:
        target_dir = harness_dir(harness)

        if target_dir is None:
            raise ValueError(f"Harness '{harness}' not found in pyproject.toml")

        env_path = target_dir / "env.yaml"

        if env_path.exists() and env_path.stat().st_size > 0:
            args.extend(["--lg-env", str(env_path)])
        args.append(str(target_dir))

    return pytest.main(args)
