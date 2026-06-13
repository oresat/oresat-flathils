from oresat_flathils.hardware import hardware


class TestHardwareModuleStructure:
    """Test hardware module structure."""

    def test_hardware_module_imports(self) -> None:
        """Test that hardware module can be imported from oresat_flathils."""
        assert hardware is not None
