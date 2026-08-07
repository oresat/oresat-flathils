"""OreSat FlatHILS Hardware Core Module.

Provides Labgrid hardware device wrappers and hardware readiness checks.
"""

import logging
from typing import TYPE_CHECKING, Any

import canopen
import pytest

if TYPE_CHECKING:
    import can


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


class CANopenNode:
    """Builds a CANopen Network on top of CANInterface() bus."""

    # Constants used for object dictionary
    H1F56_PROGRAM_SWID = 0x1F56
    H1F50_PROGRAM_DATA = 0x1F50
    H1F51_PROGRAM_CTRL = 0x1F51
    H1F57_FLASH_STATUS = 0x1F57
    NODE_ID = 0x7C

    def __init__(self, bus: can.BusABC) -> None:
        """Initialize CANopenNode with an existing python-can bus and CANopen node ID."""
        self.bus = bus
        self.network = canopen.Network(self.bus)
        self.node = self.network.add_node(self.NODE_ID, self.build_object_dictionary())

    def setup(self) -> None:
        self.network.connect()

    def teardown(self) -> None:
        self.network.disconnect()

    @staticmethod
    def build_object_dictionary() -> canopen.ObjectDictionary:
        """CANopen Object Dictionary for node."""
        object_dictionary = canopen.objectdictionary.ObjectDictionary()  # type: ignore[no-untyped-call]

        # 0x1F56: Program software identification (array of per-program SW IDs)
        program_swid_array = canopen.objectdictionary.Array(
            "Program software ID", CANopenNode.H1F56_PROGRAM_SWID
        )

        program_swid_var = canopen.objectdictionary.Variable(
            "", CANopenNode.H1F56_PROGRAM_SWID, subindex=1
        )
        program_swid_var.data_type = canopen.objectdictionary.UNSIGNED32
        program_swid_array.add_member(program_swid_var)

        object_dictionary.add_object(program_swid_array)

        # 0x1F50: Program Data (used for block downloads)
        program_data_array = canopen.objectdictionary.Array(
            "Program data", CANopenNode.H1F50_PROGRAM_DATA
        )

        program_data_var = canopen.objectdictionary.Variable(
            "", CANopenNode.H1F50_PROGRAM_DATA, subindex=1
        )
        program_data_var.data_type = canopen.objectdictionary.DOMAIN
        program_data_array.add_member(program_data_var)

        object_dictionary.add_object(program_data_array)

        # 0xF151: Program control
        program_ctrl_array = canopen.objectdictionary.Array(
            "Program control array", CANopenNode.H1F51_PROGRAM_CTRL
        )
        program_ctrl_var = canopen.objectdictionary.Variable(
            "", CANopenNode.H1F51_PROGRAM_CTRL, subindex=1
        )
        program_ctrl_var.data_type = canopen.objectdictionary.UNSIGNED8
        program_ctrl_array.add_member(program_ctrl_var)

        object_dictionary.add_object(program_ctrl_array)

        # 0xF157: Flash status
        program_flash_status_array = canopen.objectdictionary.Array(
            "Flash status", CANopenNode.H1F57_FLASH_STATUS
        )
        program_flash_status_var = canopen.objectdictionary.Variable(
            "", CANopenNode.H1F57_FLASH_STATUS, subindex=1
        )
        program_flash_status_var.data_type = canopen.objectdictionary.UNSIGNED32
        program_flash_status_array.add_member(program_flash_status_var)

        object_dictionary.add_object(program_flash_status_array)

        return object_dictionary
