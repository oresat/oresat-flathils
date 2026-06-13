from oresat_flathils.cli import cli


class TestCliModuleStructure:
    """Test module module structure."""

    def test_cli_module_imports(self) -> None:
        """Test that cli module can be imported from oresat_flathils."""
        assert cli is not None
