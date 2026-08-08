"""Configurations for mcuboot harness."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register mcuboot harness command-line options."""
    parser.addoption("--use-block-transfer", action="store_true", default=False)
    parser.addoption("--confirm-image", action="store_true", default=False)
    parser.addoption("--request-crc", action="store_true", default=False)

    # Default is 0 as the --use-block-transfer flag should be false, else it will ask for argument
    parser.addoption("--throttle-delay", action="store", default=0)
