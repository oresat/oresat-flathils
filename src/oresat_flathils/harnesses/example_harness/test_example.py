"""Example demonstrating how to write OreSat FlathHILS tests.

This module provides a basic example of testing hardware/simulation.
"""

import os
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from oresat_flathils.hardware.hardware import RP2040Device
    from oresat_flathils.simulator.simulator import BasiliskSimulator


def test_environment_variable_is_set() -> None:
    """Verify the session fixture properly set up the environment."""
    assert os.environ.get("FLATHILS_ENV_ACTIVE") == "1", "Session fixture did not run"


def test_simulator_step(flathils_sim: BasiliskSimulator) -> None:
    """Test stepping the Basilisk simulation forward."""
    assert flathils_sim.mode in ("isolated", "integrated")

    flathils_sim.step(1.0)

    # FIXME: Normally we should assert on some simulator state at this point,
    # but for now just assert the simulator stepped without crashing.
    assert True


@pytest.mark.hil
def test_rp2040_hardware(rp2040_device: RP2040Device) -> None:
    """Test connecting to the physical RP2040 hardware."""
    assert rp2040_device.is_ready

    # FIXME: Teardown happens automatically in the fixture's yield block. Is
    # there a good way to test this?
    assert True
