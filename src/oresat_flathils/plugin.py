"""Parser Plugin for FlatHILS CLI."""

import argparse
import json
from pathlib import Path
from typing import TypedDict

import pytest


class FlathilsConfig(TypedDict, total=False):
    """Shape of the JSON blob written by the flathils CLI."""

    test: str
    run_hil: bool
    can_device: str | None
    image_path: str | None
    confirm_image: bool
    request_crc: bool
    throttle_delay: int


FLATHILS_STASH_KEY: pytest.StashKey[FlathilsConfig] = pytest.StashKey()


def pytest_addoption(parser: pytest.Parser) -> None:
    """Parse arguments from CLI to pytest."""
    parser.addoption("--flathils-config", default=None, help=argparse.SUPPRESS)


def pytest_configure(config: pytest.Config) -> None:
    """Load the CLI-provided JSON config into the stash."""
    path = config.getoption("--flathils-config")
    data: FlathilsConfig = json.loads(Path(path).read_text()) if path else {}
    config.stash[FLATHILS_STASH_KEY] = data
