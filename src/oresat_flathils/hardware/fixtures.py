"""Pytest fixtures for OreSat FlatHILS Hardware Integration."""

import logging
from typing import TYPE_CHECKING

import can
import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

    import canopen

from .hardware import CANInterface, CANopenNode, RP2040Device

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
        pytest.fail("Labgrid 'target' fixture could not be found.")

    device = RP2040Device(target=target)
    device.setup()

    yield device

    log.info("Releasing RP2040 hardware...")
    device.teardown()


@pytest.fixture
def can_interface(request: pytest.FixtureRequest) -> Generator[can.BusABC]:
    """Raw python-can Bus for test cases."""
    run_hil = request.config.getoption("run_hil", default=False)
    if not run_hil:
        pytest.skip("Hardware-in-the-Loop tests require the --run-hil flag.")

    log.info("Acquiring CAN adapter hardware...")
    target = None
    try:
        target = request.getfixturevalue("target")
    except pytest.FixtureLookupError:
        pytest.fail("Labgrid 'target' Fixture was not Found.")

    device = CANInterface(target=target)
    device.setup()
    assert device.bus is not None, "CANInterface.bus was not initialized"  # noqa: S101
    yield device.bus

    log.info("Releasing CAN adapter hardware...")
    device.teardown()


@pytest.fixture
def canbus_device(can_interface: can.BusABC) -> Generator[canopen.RemoteNode]:
    """CANopen node, built directly on top of the raw CAN bus."""
    device = CANopenNode(bus=can_interface, node_id=0x7C)
    device.setup()
    assert device.node is not None, "CANopenNode.node was not initialized"  # noqa: S101
    yield device.node
    device.teardown()


@pytest.fixture
def virtual_canopen_device() -> Generator[canopen.RemoteNode]:
    """CANopen node on a virtual (no-hardware) CAN bus."""
    bus = can.interface.Bus(channel="test", interface="virtual")
    device = CANopenNode(bus=bus, node_id=0x7C)
    device.setup()
    assert device.node is not None, "CANopenNode.node was not initialized"  # noqa: S101
    yield device.node
    device.teardown()
    bus.shutdown()
