"""OreSat FlatHILS CLI Module."""

import argparse
import json
import sys
import tempfile
from pathlib import Path

import pytest

from oresat_flathils.registry import Harness, load_registry

ART = r"""
░█▀▀░█░░░█▀█░▀█▀░█░█░▀█▀░█░░░█▀▀░░░█▀▀░█░░░▀█▀
░█▀▀░█░░░█▀█░░█░░█▀█░░█░░█░░░▀▀█░░░█░░░█░░░░█░
░▀░░░▀▀▀░▀░▀░░▀░░▀░▀░▀▀▀░▀▀▀░▀▀▀░░░▀▀▀░▀▀▀░▀▀▀
"""


def validate_hil(ns: argparse.Namespace, spec: Harness, parser: argparse.ArgumentParser) -> None:
    """Verify args that are required are being passed on --run-hil are existent."""
    if not ns.run_hil:
        return

    missing = [
        a.flags[0] for a in spec.args if a.required_for_hil_test and getattr(ns, a.dest) is None
    ]
    if missing:
        parser.error(f"--run-hil for '{spec.name}' requires: {', '.join(missing)}")


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    argv = sys.argv[1:] if argv is None else argv
    registry = load_registry()

    if not registry:
        sys.exit(
            "No harnesses found via the 'flathils.harnesses' entry point.\n"
            "This usually means the package needs reinstalling after a pyproject.toml change:\n"
            "    pip install -e .\n"
        )

    # Build the parser in a single pass using subparsers
    parser = argparse.ArgumentParser(prog="flathils", description="OreSat FlatHILS Test CLI")
    subparsers = parser.add_subparsers(
        dest="args",
        required=True,
        title="Harnesses",
        metavar="<harness>",
        help="Name of the harness to load.",
    )

    # Dynamically generate a sub-command for each harness
    for name, spec in registry.items():
        sub_parser = subparsers.add_parser(name, help=f"Run tests for {name}")
        sub_parser.add_argument(
            "--run-hil",
            action="store_true",
            default=False,
            help="Run Hardware-in-the-Loop (HIL) tests alongside isolated software tests.",
        )
        for arg in spec.args:
            sub_parser.add_argument(*arg.flags, dest=arg.dest, **arg.kwargs)

    # Parse all arguments at once
    ns, extra_pytest_args = parser.parse_known_args(argv)
    spec = registry[ns.args]

    validate_hil(ns, spec, parser)

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(vars(ns), f)
        config_path = Path(f.name)

    try:
        return pytest.main(
            [spec.test_path, "--flathils-config", str(config_path), *extra_pytest_args]
        )
    finally:
        config_path.unlink()


if __name__ == "__main__":
    sys.exit(main())
