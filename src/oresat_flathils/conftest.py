"""Global configuration for FlatHILS device testing."""

import logging
import os
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

from oresat_flathils.hardware.fixtures import (
    bootloader_node,
    can_device,
    canbus,
    rp2040_device,
)
from oresat_flathils.harness_args import HARNESSES
from oresat_flathils.simulator.fixtures import flathils_sim

log = logging.getLogger()

__all__ = [
    "bootloader_node",
    "can_device",
    "canbus",
    "flathils_environment",
    "flathils_sim",
    "rp2040_device",
]


def pytest_addoption(parser: pytest.Parser) -> None:
    """Get arguments from harness_args for pytest to use."""
    for add_fn in HARNESSES.values():
        add_fn(parser)


@pytest.fixture(scope="session", autouse=True)
def flathils_environment() -> Generator[None]:
    """Set the pytest environment."""
    log.info("Setting up Example Environment ...")
    os.environ["FLATHILS_ENV_ACTIVE"] = "1"
    yield
    log.info("Tearing down Example Environment ...")
    os.environ.pop("FLATHILS_ENV_ACTIVE", None)
