from oresat_flathils.simulator import simulator


class TestSimulatorModuleStructure:
    """Test module module structure."""

    def test_simulator_module_imports(self) -> None:
        """Test that simulator module can be imported from oresat_flathils."""
        assert simulator is not None
