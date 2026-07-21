"""Pytest fixtures for OreSat FlatHILS Hardware Integration."""

import logging
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

from .hardware import CANBus, RP2040Device

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

@pytest.fixture
def canbus_device(request: pytest.FixtureRequest) -> Generator[CANBus]:
    """CANopen device wrapper for test cases."""
    run_hil = request.config.getoption("run_hil", default=False)
    if not run_hil:
        pytest.skip("Hardware-in-the-Loop tests require the --run-hil flag.")

    log.info("Acquiring CAN adapter hardware...")
    target = None
    try:
        target = request.getfixturevalue("target")
    except pytest.FixtureLookupError:
        log.warning("Labgrid 'target' fixture could not be found.")

    device = CANBus(target=target)
    device.setup()
    yield device
    log.info("Releasing CAN adapter hardware...")
    device.teardown()
