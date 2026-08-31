"""OreSat FlatHILS CLI Module."""

import sys

import pytest

ART = r"""
░█▀▀░█░░░█▀█░▀█▀░█░█░▀█▀░█░░░█▀▀░░░█▀▀░█░░░▀█▀
░█▀▀░█░░░█▀█░░█░░█▀█░░█░░█░░░▀▀█░░░█░░░█░░░░█░
░▀░░░▀▀▀░▀░▀░░▀░░▀░▀░▀▀▀░▀▀▀░▀▀▀░░░▀▀▀░▀▀▀░▀▀▀
"""


def main() -> None:
    """CLI entrypoint."""
    argv = sys.argv[1:]

    if not argv:
        sys.stdout.write(ART)
        sys.exit(pytest.main(["--help"]))

    if "-h" in argv or "--help" in argv:
        sys.stdout.write(ART)

    sys.exit(pytest.main(argv))


if __name__ == "__main__":
    main()
