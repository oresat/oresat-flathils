from oresat_flathils.core import test_runner
from oresat_flathils.core import sim_only_runner

class TestTestRunnerModuleStructure:
    def test_test_runner_module_imports(self) -> None:
        assert test_runner is not None

    def test_sim_only_module_imports(self) -> None:
        assert sim_only_runner is not None
