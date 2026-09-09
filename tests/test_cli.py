"""Tests for oresat_flathils.cli."""

from oresat_flathils.simulator import simulator


class TestSimulatorModuleStructure:
    def test_simulator_module_imports(self) -> None:
        assert simulator is not None
