"""Tests for oresat_flathils.cli."""

from unittest.mock import MagicMock

import pytest

from oresat_flathils.cli.main import ART, main


@pytest.fixture
def mock_pytest_main(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Mock (invoke) a CLI run through cli/main.py."""
    mock = MagicMock(return_value=0)
    monkeypatch.setattr(pytest, "main", mock)
    return mock


class TestCliModuleStructure:
    def test_cli_module_imports(self) -> None:
        assert main is not None


class TestCliNoArgs:
    def test_no_args_behavior(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
        mock_pytest_main: MagicMock,
    ) -> None:
        """Without args, it should print ART, call pytest help, and exit safely."""
        monkeypatch.setattr("sys.argv", ["flathils"])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code in (0, None)
        assert ART in capsys.readouterr().out
        mock_pytest_main.assert_called_once_with(["--help"])

    def test_no_args_exit_code_is_propagating(
        self, monkeypatch: pytest.MonkeyPatch, mock_pytest_main: MagicMock
    ) -> None:
        """Any invocation without any args should propagate pytest's exit code."""
        mock_pytest_main.return_value = 3
        monkeypatch.setattr("sys.argv", ["flathils"])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 3


class TestCliHelpArgs:
    @pytest.mark.parametrize("help_flag", ["-h", "--help"])
    def test_help_args_behavior(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
        mock_pytest_main: MagicMock,
        help_flag: str,
    ) -> None:
        """Help flags should print ART before handing off to pytest."""
        monkeypatch.setattr("sys.argv", ["flathils", help_flag])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code in (0, None)
        assert ART in capsys.readouterr().out
        mock_pytest_main.assert_called_once_with([help_flag])


class TestCliOtherArgs:
    def test_other_args_forwarded_unmodified_without_art(
        self,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture,
        mock_pytest_main: MagicMock,
    ) -> None:
        """Normal pytest args pass through unmodified without printing ART."""
        monkeypatch.setattr("sys.argv", ["flathils", "tests/", "-v", "-k", "smoke"])

        with pytest.raises(SystemExit):
            main()

        assert ART not in capsys.readouterr().out
        mock_pytest_main.assert_called_once_with(["tests/", "-v", "-k", "smoke"])


class TestCliUnknownArgs:
    def test_main_propagates_pytest_usage_error_exit_code(
        self, monkeypatch: pytest.MonkeyPatch, mock_pytest_main: MagicMock
    ) -> None:
        """Confirm main() doesn't swallow pytest's own exit code for bad args."""
        # Mocking the usage error code directly prevents a nested pytest execution
        mock_pytest_main.return_value = pytest.ExitCode.USAGE_ERROR
        monkeypatch.setattr("sys.argv", ["flathils", "--this-flag-does-not-exist"])

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == pytest.ExitCode.USAGE_ERROR
