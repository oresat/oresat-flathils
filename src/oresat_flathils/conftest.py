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
from oresat_flathils.plugin import FLATHILS_STASH_KEY
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
def run_hil(request: pytest.FixtureRequest) -> bool:
    return request.config.stash[FLATHILS_STASH_KEY].get("run_hil", False)


@pytest.fixture
def can_device(request: pytest.FixtureRequest) -> str | None:
    return request.config.stash[FLATHILS_STASH_KEY].get("can_device")


@pytest.fixture
def image_path(request: pytest.FixtureRequest) -> str | None:
    return request.config.stash[FLATHILS_STASH_KEY].get("image_path")


@pytest.fixture
def confirm_image(request: pytest.FixtureRequest) -> bool:
    return request.config.stash[FLATHILS_STASH_KEY].get("confirm_image", False)


@pytest.fixture
def request_crc(request: pytest.FixtureRequest) -> bool:
    return request.config.stash[FLATHILS_STASH_KEY].get("request_crc", False)


@pytest.fixture
def throttle_delay(request: pytest.FixtureRequest) -> int:
    return request.config.stash[FLATHILS_STASH_KEY].get("throttle_delay", 0)


@pytest.fixture(scope="session", autouse=True)
def flathils_environment() -> Generator[None]:
    """Set the pytest environment."""
    log.info("Setting up Example Environment ...")
    os.environ["FLATHILS_ENV_ACTIVE"] = "1"
    yield
    log.info("Tearing down Example Environment ...")
    os.environ.pop("FLATHILS_ENV_ACTIVE", None)
