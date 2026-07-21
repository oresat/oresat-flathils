"""Test configuration for Vulcan CAN harness."""

import logging

from oresat_flathils.hardware.fixtures import canbus_device

log = logging.getLogger("vulcan_harness")

__all__ = ["canbus_device"]