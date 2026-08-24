"""Pytest fixtures for OreSat FlatHILS Hardware Integration."""

import logging
from typing import TYPE_CHECKING

import can
import canopen
import pytest
from labgrid.resource import NetworkInterface

if TYPE_CHECKING:
    from collections.abc import Generator

    from labgrid import Target

from .hardware import CANopenNode, RP2040Device, SolarSimulatorDevice

log = logging.getLogger("hardware.fixtures")


@pytest.fixture
def solar_sim_device(request: pytest.FixtureRequest):
    if not request.config.getoption("run_hil", default=False):
        pytest.skip("Hardware-in-the-Loop tests require the --run-hil flag.")

    log.info("Acquiring Solar Simulator hardware...")

    target = None
    try:
        target = request.getfixturevalue("target")
    except pytest.FixtureLookupError:
        pytest.fail("Labgrid 'target' fixture could not be found.")

    device = SolarSimulatorDevice(target=request.getfixturevalue("target"))
    device.setup()

    yield device

    log.info("Releasing Solar Simulator hardware...")
    device.teardown()


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
def canbus(request: pytest.FixtureRequest, target: Target) -> Generator[can.BusABC]:
    """Raw python-can Bus for test cases."""
    run_hil = request.config.getoption("run_hil", default=False)
    if not run_hil:
        pytest.skip("Hardware-in-the-Loop tests require the --run-hil flag.")

    iface = target.get_resource(NetworkInterface)
    with can.Bus(channel=iface.ifname, interface="socketcan") as bus:
        yield bus


@pytest.fixture
def bootloader_node(canbus: can.BusABC) -> Generator[canopen.RemoteNode]:
    """CANopen node, built directly on top of the raw CAN bus."""
    node_id = 0x7C
    with canopen.Network(canbus) as network:
        network.connect()
        yield network.add_node(node_id, CANopenNode.build_object_dictionary())
