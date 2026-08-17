"""Configurations for mcuboot harness."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register mcuboot harness command-line options."""
    parser.addoption(
        "--confirm-image",
        action="store_true",
        default=False,
        help="Confirm the new image after a successful boot instead of leaving it pending.",
    )
    parser.addoption(
        "--request-crc",
        action="store_true",
        default=False,
        help="Request a CRC check of the image before finalizing the transfer.",
    )
    parser.addoption(
        "--throttle-delay",
        action="store",
        default=0,
        help="Delay in milliseconds between transfer chunks, to throttle bandwidth.",
    )
    parser.addoption(
        "--image-path",
        action="store",
        default=None,
        help="Path to the firmware image file to flash.",
    )
