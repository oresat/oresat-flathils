"""Global confiuguration for FlatHILS device testing."""

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


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom command line options to pytest."""
    parser.addoption(
        "--run-hil",
        action="store_true",
        default=False,
        help="Run Hardware-in-the-Loop (HIL) tests alongside isolated software tests.",
    )

    """ Args for CAN/ Booloader Harness """
    parser.addoption(
        "--can-device",
        action="store",
        default=None,
        help="CAN device to use for HIL testing",
    )

    """ Args for Bootloader Harness """
    parser.addoption(
        "--confirm-image",
        action="store_true",
        default=False,
    )
    parser.addoption(
        "--request-crc",
        action="store_true",
        default=False,
    )
    parser.addoption(
        "--throttle-delay",
        action="store",
        default=0,
    )
    parser.addoption(
        "--image-path",
        action="store",
        default=None,
    )


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
