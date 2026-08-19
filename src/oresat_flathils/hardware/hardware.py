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

        CANopenNode._add_program_entry(
            object_dictionary,
            name="Program software ID",
            index=CANopenNode.H1F56_PROGRAM_SWID,
            data_type=canopen.objectdictionary.UNSIGNED32,
        )  # 0x1F56: Program software identification.

        CANopenNode._add_program_entry(
            object_dictionary,
            name="Program data",
            index=CANopenNode.H1F50_PROGRAM_DATA,
            data_type=canopen.objectdictionary.DOMAIN,
        )  # 0x1F50: Program data, controls block stream of data.

        CANopenNode._add_program_entry(
            object_dictionary,
            name="Program control array",
            index=CANopenNode.H1F51_PROGRAM_CTRL,
            data_type=canopen.objectdictionary.UNSIGNED8,
        )  # 0xF151: Program control, controls FW update process.

        CANopenNode._add_program_entry(
            object_dictionary,
            name="Flash status",
            index=CANopenNode.H1F57_FLASH_STATUS,
            data_type=canopen.objectdictionary.UNSIGNED32,
        )  # 0xF157: Flash status, tells if update is progressing or errored.

        return object_dictionary

    @staticmethod
    def _add_program_entry(
        object_dictionary: canopen.ObjectDictionary,
        *,
        name: str,
        index: int,
        data_type: int,
    ) -> None:
        """Add a single-member array entry to the object dictionary."""
        array = canopen.objectdictionary.Array(name, index)
        variable = canopen.objectdictionary.Variable("", index, subindex=1)
        variable.data_type = data_type
        array.add_member(variable)
        object_dictionary.add_object(array)
