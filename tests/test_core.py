from oresat_flathils.core import runner


class TestTestRunnerModuleStructure:
    def test_test_runner_module_imports(self) -> None:
        assert runner is not None
