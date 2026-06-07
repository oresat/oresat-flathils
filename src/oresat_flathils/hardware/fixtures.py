"""Pytest fixtures for OreSat FlatHILS Hardware Integration."""
import logging
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

from .core import RP2040Device

log = logging.getLogger("hardware.fixtures")


@pytest.fixture
def rp2040_device(request: pytest.FixtureRequest) -> Generator[RP2040Device]:
    """RP2040 device wrapper for test cases."""
    run_hil = request.config.getoption("--run-hil", default = False)

    if not run_hil:
        pytest.skip("Hardware-in-the-Loop tests require the --run-hil flag.")

    log.info("Acquiring RP2040 hardware...")

    target = None
    if "target" in request.fixturenames:
        target = request.getfixturevalue("target")
    else:
        log.warning("Labgrid 'target' fixture found but could not be loaded.")

    device = RP2040Device(target = target)
    device.setup()

    yield device

    log.info("Releasing RP2040 hardware...")
    device.teardown()
