"""OreSat FlatHILS Hardware Core Module.

Provides Labgrid hardware device wrappers and hardware readiness checks.
"""

import logging
from typing import TYPE_CHECKING, Any

import can
import canopen
import pytest
from labgrid.resource import NetworkInterface

if TYPE_CHECKING:
    from labgrid import Target

H1F56_PROGRAM_SWID = 0x1F56

log = logging.getLogger("hardware.core")


class Device:
    """Base class for PSAS hardware devices."""

    # FIXME: Don't just silence this type check.
    def __init__(self, target: Any = None) -> None:  # noqa: ANN401
        """Initialize the device with a Labgrid Target.

        Docs: https://labgrid.readthedocs.io/en/stable/_modules/labgrid/target.html
        """
        self.target = target
        self.is_ready = False

    def setup(self) -> None:
        """Acquire hardware device and verify readiness."""
        raise NotImplementedError

    def teardown(self) -> None:
        """Release hardware device and return to a safe neutral state."""
        raise NotImplementedError


class RP2040Device(Device):
    """Wrapper for RP2040 (Raspberry Pi Pico) device.

    While this may be a useful start for RasPi Pico-driven devices, the intention
    here is to provide an example usecase that inherits from the Device base class
    to establish the development pattern. This class can be removed after actual
    PSAS lab hardware device classes are written.
    """

    def setup(self) -> None:
        """Ensure RP2040 Device is available and ready."""
        log.debug("Checking RP2040 for readiness ...")

        if not self.target:
            pytest.skip("Failed to acquire Labgrid RP2040 target")
            return

        self.serial = self.target.get_driver("SerialDriver")
        self.target.activate(self.serial)

        if not self._ping():
            pytest.fail("RP2040 did not respond to readiness check")
            return

        self.is_ready = True

    def _ping(self) -> bool:
        """Send a lightweight command and confirm the RP2040 responds."""
        self.serial.write(b"PING\n")
        response = self.serial.read(timeout=2.0)
        return bool(response.strip() == b"PONG")

    def teardown(self) -> None:
        """Deactivate and clean up."""
        if self.target:
            self.target.deactivate()

        self.is_ready = False


class CANInterface(Device):
    """Labgrid target and raw python-can bus."""

    def __init__(self, target: Target | None = None) -> None:
        """Initialize CANInterface with a Labgrid target."""
        super().__init__(target)
        self.bus: can.BusABC | None = None

    def setup(self) -> None:
        if not self.target:
            pytest.fail("Failed to acquire Labgrid CAN adapter target")
            return
        iface = self.target.get_resource(NetworkInterface)
        self.bus = can.interface.Bus(channel=iface.ifname, interface="socketcan")
        self.is_ready = True

    def teardown(self) -> None:
        if self.bus:
            self.bus.shutdown()
        self.is_ready = False


class CANopenNode:
    """Builds a CANopen Network on to of CANInterface() bus."""

    def __init__(self, bus: can.BusABC, node_id: int = 0x7C) -> None:
        """Initialize CANopenNode with an existing python-can bus and CANopen node ID."""
        self.bus = bus
        self.node_id = node_id
        self.network: canopen.Network | None = None
        self.node: canopen.RemoteNode | None = None

    def setup(self) -> None:
        self.network = canopen.Network()
        self.network.bus = self.bus
        self.network.notifier = can.Notifier(self.bus, self.network.listeners, 1.0)
        self.node = self.network.add_node(self.node_id, self._object_dictionary())

    def teardown(self) -> None:
        if self.network:
            if self.network.notifier:
                self.network.notifier.stop()
            self.network.disconnect()
        self.is_ready = False

    @staticmethod
    def _object_dictionary() -> canopen.ObjectDictionary:
        """CANopen Object Dictionary for node.

        Currently defines an object 0x1F56
        which is the program Software identification address used on CANopen node running on Zephyr.
        This is an array because a node may support multiple programs
        as in, it makes sure future expandability within FlatHILS CAN is easier.
        """
        object_dictionary = canopen.objectdictionary.ObjectDictionary()  # type: ignore[no-untyped-call]

        # 0x1F56: Program software identification (array of per-program SW IDs)
        program_swid_array = canopen.objectdictionary.Array(
            "Program software ID", H1F56_PROGRAM_SWID
        )

        # Subindex 1: software ID for program 1
        program_swid_var = canopen.objectdictionary.Variable("", H1F56_PROGRAM_SWID, subindex=1)
        program_swid_var.data_type = canopen.objectdictionary.UNSIGNED32
        program_swid_array.add_member(program_swid_var)

        object_dictionary.add_object(program_swid_array)

        return object_dictionary
