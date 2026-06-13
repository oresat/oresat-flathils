from oresat_flathils.core import test_runner


class TestTestRunnerModuleStructure:
    """Test module module structure."""

    def test_test_runner_module_imports(self) -> None:
        """Test that test_runner module can be imported from oresat_flathils."""
        assert test_runner is not None
