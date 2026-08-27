"""CLI-visible harness registry and argument definitions."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    import pytest

HARNESSES: dict[str, Callable[[pytest.Parser], None]] = {}

REQUIRED_OPTIONS: dict[str, list[str]] = {}


def harness(
    name: str,
    requires: list[str] | None = None,
) -> Callable[[Callable[[pytest.Parser], None]], Callable[[pytest.Parser], None]]:
    """Register a function as a harness's argument adder."""

    def decorator(fn: Callable[[pytest.Parser], None]) -> Callable[[pytest.Parser], None]:
        HARNESSES[name] = fn
        if requires:
            REQUIRED_OPTIONS[name] = requires
        return fn

    return decorator


@harness("run-hil")
def add_hil_args(parser: pytest.Parser) -> None:
    """HIL harness args."""
    parser.addoption(
        "--run-hil",
        action="store_true",
        default=False,
        help="Run Hardware-in-the-Loop (HIL) tests alongside isolated software tests.",
    )


@harness("can-harness", requires=["can_device"])
def add_can_args(parser: pytest.Parser) -> None:
    """CAN harness args."""
    parser.addoption(
        "--can-device",
        action="store",
        default=None,
        help="CAN device to use for HIL testing (Required for harnesses that use CAN.)",
    )


@harness("bootloader-harness", requires=["can_device", "image_path"])
def add_bootloader_args(parser: pytest.Parser) -> None:
    """Bootloader harness args."""
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
        type=float,
        help="Delay in milliseconds between transfer chunks, to throttle bandwidth.",
    )
    parser.addoption(
        "--image-path",
        action="store",
        default=None,
        help="Path to the firmware image file to flash.",
    )
