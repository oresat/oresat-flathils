"""Shared pytest configuration for OreSat FlatHILS."""

import pytest  # noqa: TC002 -- pytest evaluates this hook's annotations at runtime, this can be ignored


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add custom command line options to pytest."""
    parser.addoption(
        "--run-hil",
        action="store_true",
        default=False,
        help="Run Hardware-in-the-Loop (HIL) tests alongside isolated software tests.",
    )
