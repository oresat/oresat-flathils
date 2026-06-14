from oresat_flathils.simulator import simulator


class TestSimulatorModuleStructure:
    def test_simulator_module_imports(self) -> None:
        assert simulator is not None
