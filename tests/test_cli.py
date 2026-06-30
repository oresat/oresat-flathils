from oresat_flathils.cli import main


class TestCliModuleStructure:
    def test_cli_module_imports(self) -> None:
        assert main is not None
