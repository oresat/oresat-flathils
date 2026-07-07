"""Pytest fixtures for OreSat FlatHILS Hardware Integration."""

import logging
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

from .hardware import RP2040Device

log = logging.getLogger("hardware.fixtures")


@pytest.fixture
def rp2040_device(request: pytest.FixtureRequest) -> Generator[RP2040Device]:
    """RP2040 device wrapper for test cases."""
    run_hil = request.config.getoption("run_hil", default=False)

    if not run_hil:
        pytest.skip("Hardware-in-the-Loop tests require the --run-hil flag.")

    log.info("Acquiring RP2040 hardware...")

    target = None
    try:
        target = request.getfixturevalue("target")
    except pytest.FixtureLookupError:
        log.warning("Labgrid 'target' fixture could not be found.")

    device = RP2040Device(target=target)
    device.setup()

    yield device

    log.info("Releasing RP2040 hardware...")
    device.teardown()
