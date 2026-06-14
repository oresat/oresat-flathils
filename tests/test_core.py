from oresat_flathils.core import test_runner


class TestTestRunnerModuleStructure:
    def test_test_runner_module_imports(self) -> None:
        assert test_runner is not None
