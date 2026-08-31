import time
from pathlib import Path
from typing import TYPE_CHECKING, TypedDict

import pytest

from oresat_flathils.hardware.hardware import CANopenNode

if TYPE_CHECKING:
    import can
    import canopen
    from can import Message
    from canopen.sdo.base import SdoVariable

DOWNLOAD_BUFFER_SIZE = 889
STATUS_TIMEOUT_S = 30.0
BOOTUP_TIMEOUT_S = 20.0
SDO_TIMEOUT_S = 3.0
SDO_RETRIES = 3

PROGRAM_CTRL_STOP = 0x00
PROGRAM_CTRL_START = 0x01
PROGRAM_CTRL_CLEAR = 0x03
PROGRAM_CTRL_ZEPHYR_CONFIRM = 0x80


class FlashCliArgs(TypedDict):
    """Typed shape of the CLI-derived flash arguments."""

    throttle_delay: float
    confirm_image: bool
    request_crc: bool
    image_path: str | None
    can_device: str | None


@pytest.fixture(scope="session")
def flash_cli_args(pytestconfig: pytest.Config) -> FlashCliArgs:
    """Pytest arguments, uses CLI. image_path is required."""
    return {
        "throttle_delay": float(pytestconfig.getoption("--throttle-delay")),
        "confirm_image": bool(pytestconfig.getoption("--confirm-image")),
        "request_crc": bool(pytestconfig.getoption("--request-crc")),
        "image_path": pytestconfig.getoption("--image-path"),
        "can_device": pytestconfig.getoption("--can-device"),
    }


def get_bin_path(path: str | None) -> Path:
    """Get firmware binary path and resolve within CLI."""
    if not path:
        pytest.fail("No argument found for --image-path.")

    zephyr_img_path = Path(path).expanduser().resolve()
    if not zephyr_img_path.is_file():
        pytest.fail(f"Firmware file was not found on: {zephyr_img_path}")

    return zephyr_img_path


def wait_flash_status_ok(flash_sdo: SdoVariable, timeout_s: float) -> int:
    """Wait for an OK from zephyr to start the flash process."""
    end = time.time() + timeout_s
    status = int(flash_sdo.raw)

    while status != 0 and time.time() < end:
        time.sleep(0.1)
        status = int(flash_sdo.raw)

    return status


def throttle_bus_send(
    monkeypatch: pytest.MonkeyPatch,
    bus: can.BusABC,
    throttle_delay: float,
) -> None:
    """Wrap bus.send so each call sleeps for throttle_delay afterward."""
    original_send = bus.send

    def throttle_send(msg: Message, timeout: float | None = None) -> None:
        original_send(msg, timeout)
        time.sleep(throttle_delay)

    monkeypatch.setattr(bus, "send", throttle_send)


def test_zephyr_flash_device(
    monkeypatch: pytest.MonkeyPatch,
    bootloader_node: canopen.RemoteNode,
    flash_cli_args: FlashCliArgs,
) -> None:
    """Flash a zephyr image using CANopen."""
    throttle_delay = flash_cli_args["throttle_delay"]
    confirm_image = flash_cli_args["confirm_image"]
    request_crc = flash_cli_args["request_crc"]
    path = flash_cli_args["image_path"]
    is_throttling: bool = False
    bin_path = get_bin_path(path)

    size = bin_path.stat().st_size

    if throttle_delay != 0:
        is_throttling = True
        bus = bootloader_node.network.bus
        if bus is None:
            pytest.fail("CAN not available for block transfer")
        throttle_bus_send(monkeypatch, bus, throttle_delay)

    bootloader_node.sdo.MAX_RETRIES = SDO_RETRIES
    bootloader_node.sdo.RESPONSE_TIMEOUT = SDO_TIMEOUT_S

    data_sdo = bootloader_node.sdo[CANopenNode.H1F50_PROGRAM_DATA][1]
    ctrl_sdo = bootloader_node.sdo[CANopenNode.H1F51_PROGRAM_CTRL][1]
    flash_sdo = bootloader_node.sdo[CANopenNode.H1F57_FLASH_STATUS][1]

    bootloader_node.nmt.state = "PRE-OPERATIONAL"

    ctrl_sdo.raw = PROGRAM_CTRL_STOP
    ctrl_sdo.raw = PROGRAM_CTRL_CLEAR

    with bin_path.open("rb") as infile:
        outfile = data_sdo.open(
            "wb",
            buffering=DOWNLOAD_BUFFER_SIZE,
            size=size,
            request_crc_support=request_crc,
            block_transfer=is_throttling,
        )
        outfile.write(infile.read())
        outfile.close()

    status = wait_flash_status_ok(flash_sdo, STATUS_TIMEOUT_S)
    if status != 0:
        pytest.fail(f"FLASH failed with status 0x{status:08X}")

    ctrl_sdo.raw = PROGRAM_CTRL_START
    bootloader_node.nmt.wait_for_bootup(timeout=BOOTUP_TIMEOUT_S)

    if confirm_image:
        bootloader_node.nmt.state = "PRE-OPERATIONAL"
        ctrl_sdo.raw = PROGRAM_CTRL_ZEPHYR_CONFIRM
