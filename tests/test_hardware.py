from oresat_flathils.hardware import hardware


class TestHardwareModuleStructure:
    def test_hardware_module_imports(self) -> None:
        assert hardware is not None
