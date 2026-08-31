"""Global configuration for FlatHILS device testing."""

import logging
import os
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

from oresat_flathils.hardware.fixtures import (
    bootloader_node,
    canbus,
    rp2040_device,
)
from oresat_flathils.simulator.fixtures import flathils_sim

log = logging.getLogger("can_harness")

__all__ = [
    "bootloader_node",
    "canbus",
    "flathils_environment",
    "flathils_sim",
    "rp2040_device",
]


@pytest.fixture
def can_device(request: pytest.FixtureRequest) -> str | None:
    return str(request.config.getoption("--can-device"))


@pytest.fixture(scope="session", autouse=True)
def flathils_environment() -> Generator[None]:
    """Set the pytest environment."""
    log.info("Setting up Example Environment ...")
    os.environ["FLATHILS_ENV_ACTIVE"] = "1"
    yield
    log.info("Tearing down Example Environment ...")
    os.environ.pop("FLATHILS_ENV_ACTIVE", None)
