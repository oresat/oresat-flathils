"""Global confiuguration for FlatHILS device testing."""

import logging
import os
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

from oresat_flathils.hardware.fixtures import (
    can_interface,
    canbus_device,
    rp2040_device,
    virtual_canopen_device,
)
from oresat_flathils.simulator.fixtures import flathils_sim

log = logging.getLogger("can_harness")

"""
    This allows for all harnesses to have on single global configuration file
    rather than having all harnesses have individual conftests, which can get cluttered.

    this also fixes the duplicate --run-hil argument from being a problem.
"""
__all__ = [
    "can_interface",
    "canbus_device",
    "flathils_environment",
    "flathils_sim",
    "rp2040_device",
    "virtual_canopen_device",
]


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom command line options to pytest."""
    parser.addoption(
        "--run-hil",
        action="store_true",
        default=False,
        help="Run Hardware-in-the-Loop (HIL) tests alongside isolated software tests.",
    )


@pytest.fixture(scope="session", autouse=True)
def flathils_environment() -> Generator[None]:
    """Set the pytest environment."""
    log.info("Setting up Example Environment ...")
    os.environ["FLATHILS_ENV_ACTIVE"] = "1"

    yield

    log.info("Tearing down Example Environment ...")
    os.environ.pop("FLATHILS_ENV_ACTIVE", None)
