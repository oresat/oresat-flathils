from oresat_flathils.cli import cli


class TestCliModuleStructure:
    def test_cli_module_imports(self) -> None:
        assert cli is not None
