"""Pytest fixtures for OreSat FlatHILS Hardware Integration."""

import logging
from typing import TYPE_CHECKING

import can
import canopen
import pytest

if TYPE_CHECKING:
    from collections.abc import Generator


from .hardware import CANopenNode, RP2040Device

log = logging.getLogger("hardware.fixtures")


@pytest.fixture
def can_device(pytestconfig: pytest.Config) -> str:
    """Pytest argument for CAN device."""
    return str(pytestconfig.getoption("--can_device"))


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
def canbus(request: pytest.FixtureRequest, can_device: str) -> Generator[can.BusABC]:
    """Raw python-can Bus for test cases."""
    run_hil = request.config.getoption("run_hil", default=False)
    if not run_hil:
        pytest.skip("Hardware-in-the-Loop tests require the --run-hil flag.")

    if not can_device:
        pytest.skip("Harnesses with CAN require a CAN connection")

    with can.Bus(channel=can_device, interface="socketcan") as bus:
        yield bus


@pytest.fixture
def bootloader_node(canbus: can.BusABC) -> Generator[canopen.RemoteNode]:
    """CANopen node, built directly on top of the raw CAN bus."""
    node_id = 0x7C
    with canopen.Network(canbus) as network:
        network.connect()
        yield network.add_node(node_id, CANopenNode.build_object_dictionary())
