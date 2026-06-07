"""OreSat FlatHILS CLI Module."""
import argparse
import sys

from oresat_flathils.core.test_runner import run_pytest


def main(argv: list[str] | None = None) -> int:
    """Entrypoint for the OreSat FlatHILS CLI."""
    if argv is None:
        argv = sys.argv[1:]

    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "test":
        pytest_args = list(args.pytest_args)

        if pytest_args[:1] == ["--"]:
            pytest_args = pytest_args[1:]

        try:
            return run_pytest(pytest_args = pytest_args, harness = args.harness)
        except (LookupError, ValueError) as exception:
            sys.stderr.write(f"flathils test: {exception}\n")

        return 2

    parser.print_help()

    return 1


def _build_parser() -> argparse.ArgumentParser:
    """Build the CLI tool options."""
    parser = argparse.ArgumentParser(prog = 'OreSat FlatHILS CLI',
                                     description = 'The OreSat FlatHILS Command-Line Interface.',
                                     epilog = 'Happy Testing! 🎂')

    subparsers = parser.add_subparsers(dest = "command", required = True)

    # Test parser
    test_parser = subparsers.add_parser(
        "test",
        help = "Run pytest with FlatHILS environment setup.",
    )

    test_parser.add_argument(
        "--harness",
        required = True,
        help = "Select a test harness name (configured in pyproject.toml).",
    )

    test_parser.add_argument(
        "--pytest-args",
        nargs = argparse.REMAINDER,
        default = [],
        help = "Arguments forwarded to pytest (prefix with --).",
    )

    return parser
