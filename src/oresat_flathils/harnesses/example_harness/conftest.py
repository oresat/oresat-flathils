"""Test Configuation file for Example Harness."""

import logging
import os
from typing import TYPE_CHECKING

import pytest

from oresat_flathils.hardware.fixtures import rp2040_device
from oresat_flathils.simulator.fixtures import flathils_sim

if TYPE_CHECKING:
    from collections.abc import Generator

log = logging.getLogger("example_harness")


@pytest.fixture(scope="session", autouse=True)
def flathils_environment() -> Generator[None]:
    """Set the pytest environment."""
    log.info("Setting up Example Environment ...")
    os.environ["FLATHILS_ENV_ACTIVE"] = "1"

    yield

    log.info("Tearing down Example Environment ...")
    os.environ.pop("FLATHILS_ENV_ACTIVE", None)
