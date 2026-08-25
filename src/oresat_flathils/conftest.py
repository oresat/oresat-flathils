"""Global confiuguration for FlatHILS device testing."""

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
    solar_sim_device,
)
from oresat_flathils.simulator.fixtures import flathils_sim

log = logging.getLogger("can_harness")

__all__ = [
    "bootloader_node",
    "can_device",
    "canbus",
    "flathils_environment",
    "flathils_sim",
    "rp2040_device",
    "solar_sim_device",
]


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom command line options to pytest."""
    add_hil_args(parser)
    add_can_args(parser)
    add_bootloader_args(parser)


def add_hil_args(parser: pytest.Parser) -> None:
    """Add HIL-related command line options."""
    parser.addoption(
        "--run-hil",
        action="store_true",
        default=False,
        help="Run Hardware-in-the-Loop (HIL) tests alongside isolated software tests.",
    )


def add_can_args(parser: pytest.Parser) -> None:
    """CAN/bootloader harness args."""
    parser.addoption(
        "--can-device",
        action="store",
        default=None,
        help="CAN device to use for HIL testing",
    )


def add_bootloader_args(parser: pytest.Parser) -> None:
    """Bootloader harness args."""
    parser.addoption(
        "--confirm-image",
        action="store_true",
        default=False,
        help="Confirm the new image after a successful boot instead of leaving it pending.",
    )
    parser.addoption(
        "--request-crc",
        action="store_true",
        default=False,
        help="Request a CRC check of the image before finalizing the transfer.",
    )
    parser.addoption(
        "--throttle-delay",
        action="store",
        default=0,
        type=float,
        help="Delay in milliseconds between transfer chunks, to throttle bandwidth.",
    )
    parser.addoption(
        "--image-path",
        action="store",
        default=None,
        help="Path to the firmware image file to flash.",
    )


@pytest.fixture(scope="session", autouse=True)
def flathils_environment() -> Generator[None]:
    """Set the pytest environment."""
    log.info("Setting up Example Environment ...")
    os.environ["FLATHILS_ENV_ACTIVE"] = "1"

    yield

    log.info("Tearing down Example Environment ...")
    os.environ.pop("FLATHILS_ENV_ACTIVE", None)
