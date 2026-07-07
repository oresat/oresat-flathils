"""OreSat FlatHILS Hardware Core Module.

Provides Labgrid hardware device wrappers and hardware readiness checks.
"""

import logging
from typing import Any

import pytest

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

    def teadown(self) -> None:
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
