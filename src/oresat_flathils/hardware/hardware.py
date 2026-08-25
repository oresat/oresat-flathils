"""OreSat FlatHILS Hardware Core Module.

Provides Labgrid hardware device wrappers and hardware readiness checks.
"""

import logging
import re
import time
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


_STATUS_RE = re.compile(
    rb"LED: ([\d.]+).*Heatsink: ([\d.]+).*Cell: ([\d.]+).*"
    rb"VIOLET:(\d+)% WHITE:(\d+)% CYAN:(\d+)%\s+HAL:(\d+)%"
)

class SolarSimulatorDevice(Device):
    """Drives the Solar Simulator device over usb_cdc.data."""

    def setup(self) -> None:
        if not self.target:
            import pytest
            pytest.skip("Failed to acquire Labgrid solar-simulator target")
            return

        self.serial = self.target.get_driver("SerialDriver")
        self.target.activate(self.serial)
        # self._drain()

        # Don't gate on the boot-time READY write -- it may already have been
        # missed. Prove liveness with a real round trip instead, starting
        # from a known-safe state.
        self.set_intensity(0)
        if self.read_status(timeout=5.0) is None:
            import pytest
            pytest.fail(
                "solar simulator did not respond on usb_cdc.data -- "
                "unpowered, unflashed, or wedged from a prior bad message"
            )
        self.is_ready = True

    def set_intensity(self, percent: int) -> None:
        if not 0 <= percent <= 100:
            raise ValueError(f"intensity must be 0-100, got {percent}")
        self.serial.write(f"{percent}\n".encode())

    def read_status(self, timeout: float = 2.0) -> dict[str, Any] | None:
        line = self._read_line(timeout=timeout)
        match = _STATUS_RE.search(line)
        if not match:
            return None
        led, heatsink, cell, v, w, c, h = match.groups()
        return {
            "led_c": float(led), "heatsink_c": float(heatsink), "cell_c": float(cell),
            "violet_pct": int(v), "white_pct": int(w), "cyan_pct": int(c), "halogen_pct": int(h),
        }

    def _read_line(self, timeout: float = 2.0) -> bytes:
        """Accumulate bytes until a newline is seen or the deadline passes."""
        deadline = time.monotonic() + timeout
        buf = b""
        while time.monotonic() < deadline:
            remaining = max(deadline - time.monotonic(), 0)
            chunk = self.serial.read(timeout=remaining)
            if chunk:
                buf += chunk
                print(f"DEBUG _read_line accumulated: {buf!r}")  # temporary
                if b"\n" in buf:
                    break
        return buf

    # def _drain(self) -> None:
    #     """Discard any bytes left over from a previous session."""
    #     while True:
    #         leftover = self.serial.read(timeout=5)
    #         if not leftover:
    #             break

    # def read_status(self, timeout: float = 2.0) -> dict[str, Any] | None:
    #     line = self.serial.read(timeout=timeout)
    #     print(f"DEBUG raw read: {line!r}")
    #     match = _STATUS_RE.search(line)
    #     if not match:
    #         return None
    #     led, heatsink, cell, v, w, c, h = match.groups()
    #     return {
    #         "led_c": float(led), "heatsink_c": float(heatsink), "cell_c": float(cell),
    #         "violet_pct": int(v), "white_pct": int(w), "cyan_pct": int(c), "halogen_pct": int(h),
    #     }

    def teardown(self) -> None:
        if self.target:
            try:
                self.set_intensity(0)
            finally:
                self.target.deactivate(self.serial)
        self.is_ready = False

    # def teardown(self) -> None:
    #     if self.target:
    #         try:
    #             self.set_intensity(0)  # leave the bench safe -- run() never exits on its own
    #         finally:
    #             self.target.deactivate()
    #     self.is_ready = False


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
    DEFAULT_NODE_ID = 0x7C

    def __init__(self, bus: can.BusABC, node_id: int = DEFAULT_NODE_ID) -> None:
        """Initialize CANopenNode with an existing python-can bus and CANopen node ID."""
        self.bus = bus
        self.node_id = node_id
        self.network = canopen.Network(self.bus)
        self.node = self.network.add_node(self.node_id, self.build_object_dictionary())

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
