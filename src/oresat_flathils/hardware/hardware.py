"""OreSat FlatHILS Hardware Core Module.

Provides Labgrid hardware device wrappers and hardware readiness checks.
"""

import logging
from typing import Any

import canopen
import pytest

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

    # FIXME: Don't just silence this type check.
    def __init__(self, target: Any = None) -> None:  # noqa: ANN401
        """Initialize RP2040 device."""
        super().__init__(target)

    def setup(self) -> None:
        """Ensure RP2040 Device is available and ready."""
        log.debug("Checking RP2040 for readiness ...")

        if not self.target:
            pytest.skip("Failed to acquire Labgrid RP2040 target")

        self.serial = self.target.get_driver("SerialDriver")
        self.is_ready = True

    def teardown(self) -> None:
        """Deactivate and clean up."""
        if self.target:
            try:
                self.target.deactivate()
            except Exception:
                log.exception("Error deactivating labgrid target.")

        self.is_ready = False


class SolarSimulator(Device):
    """Wrapper for the Benchtop Solar Simulator."""

    # FIXME: Implement Solar Simulator hardware device.


class CANBus(Device):
    """Wrapper for CANopen bus interface.

    This uses the CANopen Library to provide a CAN interface using a serial-to-CAN adapter.
    This test was implemented using a CopperForge VulCAN, use other adapters at your own risk.
    """

    # FIXME: Don't just silence this type check.
    def __init__(self, target: Any = None, node_id: int = 0x7C, bitrate: int = 1_000_000) -> None:  # noqa: ANN401
        """Initialize CANBus device."""
        super().__init__(target)
        self.node_id = node_id
        self.bitrate = bitrate
        self.network: canopen.Network | None = None
        self.node: canopen.RemoteNode | None = None

    def setup(self) -> None:
        """Acquire the slcan adapter via labgrid and bring up a canopen Network."""
        log.debug("Checking CAN adapter for readiness ...")
        if not self.target:
            pytest.skip("Failed to acquire Labgrid CAN adapter target")

        self.target.activate(self.target.get_driver("SerialDriver"))
        resource = self.target.get_resource("USBSerialPort")
        port = resource.port

        self.network = canopen.Network()
        self.network.connect(interface="slcan", channel=port, bitrate=self.bitrate)
        self.node = self.network.add_node(self.node_id, self._object_dictionary())
        self.is_ready = True

    def teardown(self) -> None:
        """Disconnect the CANopen network."""
        if self.network:
            try:
                self.network.disconnect()
            except Exception:
                log.exception("Error disconnecting CAN network.")
        self.is_ready = False

    @staticmethod
    def _object_dictionary() -> canopen.ObjectDictionary:

        objdict = canopen.objectdictionary.ObjectDictionary()  # type: ignore[no-untyped-call]
        arr = canopen.objectdictionary.Array("Program software ID", H1F56_PROGRAM_SWID)
        var = canopen.objectdictionary.Variable("", H1F56_PROGRAM_SWID, subindex=1)
        var.data_type = canopen.objectdictionary.UNSIGNED32
        arr.add_member(var)
        objdict.add_object(arr)
        return objdict
