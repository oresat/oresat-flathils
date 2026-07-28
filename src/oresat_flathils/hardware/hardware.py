"""OreSat FlatHILS Hardware Core Module.

Provides Labgrid hardware device wrappers and hardware readiness checks.
"""

import logging
import time
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
        try:
            self.serial.write(b"PING\n")
            response = self.serial.read(timeout=2.0)
            return bool(response.strip() == b"PONG")
        except Exception:
            log.exception("RP2040 did not respond to ping.")
            return False

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

    This class uses the python-canopen library to interface with a a serial to CAN adapter
    via slcan. The adapter is acquired via labgrid and the CANopen network is brought up for use.
    This device wrapper was built for a Copperforge VulCAN USB-CAN adapter
    but should work with any slcan-compatible adapter.
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
        if not self.target:
            pytest.fail("Failed to acquire Labgrid CAN adapter target")
            return

        self.target.activate(self.target.get_driver("SerialDriver"))
        resource = self.target.get_resource("USBSerialPort")
        port = resource.port

        try:
            self.network = canopen.Network()
        except Exception:
            log.exception("Failed to initialize CANopen network object")
            pytest.fail("Failed to initialize CANopen network")
            return

        canopen_connect_attempts = 3
        canopen_retry_delay = 1.0  # in seconds, lets CANopen flush

        for attempt in range(1, canopen_connect_attempts + 1):
            # Attempt to connect
            try:
                self.network.connect(interface="slcan", channel=port, bitrate=self.bitrate)
                break
            except Exception:
                log.exception("CANopen Connection attempt #%d failed. Retrying...", attempt)
                try:
                    self.network.disconnect()  # Failed! attempt to disconnect before trying again.
                except Exception:
                    log.exception("Unable to disconnect CAN network after failed attempt")

                # Try again to connect, let logs flush first.
                if attempt < canopen_connect_attempts:
                    time.sleep(canopen_retry_delay)
        else:
            pytest.fail("Failed to connect to CANopen Network")
            return

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
