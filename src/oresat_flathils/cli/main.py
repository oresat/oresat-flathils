"""OreSat FlatHILS CLI Module."""

import argparse
import shlex
import sys

from oresat_flathils.core.runner import run_pytest

ART = r"""
░█▀▀░█░░░█▀█░▀█▀░█░█░▀█▀░█░░░█▀▀░░░█▀▀░█░░░▀█▀
░█▀▀░█░░░█▀█░░█░░█▀█░░█░░█░░░▀▀█░░░█░░░█░░░░█░
░▀░░░▀▀▀░▀░▀░░▀░░▀░▀░▀▀▀░▀▀▀░▀▀▀░░░▀▀▀░▀▀▀░▀▀▀
"""


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level CLI parser."""
    parser = argparse.ArgumentParser(prog="flathils", add_help=False)
    subparsers = parser.add_subparsers(dest="commands", metavar="commands: ")
    parser.add_argument(
        "--help", action="store_true", default=False, help="Show this help message and exit."
    )
    test_parser = subparsers.add_parser(
        "test", help="Run pytest with FlatHILS environment setup for a given harness."
    )
    test_parser.add_argument("harness", help="Name of the harness to load from pyproject.toml.")
    test_parser.add_argument(
        "--run-hil", action="store_true", default=False, help="Run hardware-in-the-loop tests."
    )
    test_parser.add_argument(
        "--pytest-args",
        default="",
        help='Quoted string of arguments to pass through to PyTest, e.g. --pytest-args="-v"',
    )
    return parser


def base(argv: list[str] | None = None) -> None:
    """CLI entrypoint."""
    raw_args = sys.argv[1:] if argv is None else argv

    # This is an annoying issue with pytest and argparse. click had the same issue. at one point
    # for now, allow both, but mainly point on docs to use --pytest-args
    if "--" in raw_args:
        split = raw_args.index("--")
        cli_args, passthrough_args = raw_args[:split], raw_args[split + 1 :]
    else:
        cli_args, passthrough_args = raw_args, []

    parser = build_parser()
    args, unknown = parser.parse_known_args(cli_args)

    if (not raw_args or args.help) and (args.commands is None):
        sys.stdout.write(ART)
        parser.print_help()
        sys.exit(0)

    # TODO: this command currently detects all unknows and prints this.
    # such as flathils --noncaommand returns this. it should return different messages.
    if unknown:
        sys.stderr.write(f"flathils: unrecognized arguments: {' '.join(unknown)}\n")
        sys.exit(2)

    if args.command == "test":
        pytest_args = shlex.split(args.pytest_args) + passthrough_args
        try:
            sys.exit(
                run_pytest(
                    harness=args.harness,
                    run_hil=args.run_hil,
                    pytest_args=pytest_args,
                )
            )
        except (LookupError, ValueError) as exception:
            sys.stderr.write(f"flathils test: {exception}\n")
            sys.exit(1)


if __name__ == "__main__":
    base()
