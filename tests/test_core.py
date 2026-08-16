from oresat_flathils.core import runner, sim_only_runner


class TestTestRunnerModuleStructure:
    def test_test_runner_module_imports(self) -> None:
        assert runner is not None

    def test_sim_only_module_imports(self) -> None:
        assert sim_only_runner is not None
