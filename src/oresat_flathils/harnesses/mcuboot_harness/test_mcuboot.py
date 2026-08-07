import os
import time
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from oresat_flathils.hardware.hardware import CANopenNode

if TYPE_CHECKING:
    import canopen

DOWNLOAD_BUFFER_SIZE = 889
STATUS_TIMEOUT_S = 30.0
BOOTUP_TIMEOUT_S = 20.0
SDO_TIMEOUT_S = 3.0
SDO_RETRIES = 3

PROGRAM_CTRL_STOP = 0x00
PROGRAM_CTRL_START = 0x01
PROGRAM_CTRL_CLEAR = 0x03
PROGRAM_CTRL_ZEPHYR_CONFIRM = 0x80

BIN_PATH = Path(__file__).parent / "zephyr_image" / "zephyr.signed.bin"


@pytest.fixture(scope="session")
def block_transfer(pytestconfig: pytest.Config) -> bool:
    return bool(pytestconfig.getoption("--use-block-transfer"))

@pytest.fixture(scope="session")
def throttle_delay(pytestconfig: pytest.Config) -> float:
    return float(pytestconfig.getoption("--throttle-delay"))

@pytest.fixture(scope="session")
def confirm_image(pytestconfig: pytest.Config) -> bool:
    return bool(pytestconfig.getoption("--confirm-image"))

@pytest.fixture(scope="session")
def request_crc(pytestconfig: pytest.Config) -> bool:
    return bool(pytestconfig.getoption("--request-crc"))


def wait_flash_status_ok(flash_sdo, timeout_s) -> int:
    end = time.time() + timeout_s
    status = int(flash_sdo.raw)

    while status != 0 and time.time() < end:
        time.sleep(0.1)
        status = int(flash_sdo.raw)

    return status


def test_mcuboot_flash_device(
    bootloader_node: canopen.RemoteNode, block_transfer, throttle_delay, confirm_image, request_crc
) -> None:
    """Flash a built zephyr image with CANopen."""
    if not BIN_PATH.is_file():
        pytest.fail(f"No binary file found on: {BIN_PATH}")

    size = os.path.getsize(BIN_PATH)

    node = bootloader_node.network.add_node(
        CANopenNode.NODE_ID, CANopenNode.build_object_dictionary()
    )

    if block_transfer:
        print(f"\nUsing Block transfer at a delay of {throttle_delay} sec...")
        original_send = node.network.bus.send

        def throttle_send(msg, timeout=None):
            original_send(msg, timeout)
            time.sleep(throttle_delay)

        node.network.bus.send = throttle_send

    node.sdo.MAX_RETRIES = SDO_RETRIES
    node.sdo.RESPONSE_TIMEOUT = SDO_TIMEOUT_S

    data_sdo = node.sdo[CANopenNode.H1F50_PROGRAM_DATA][1]
    ctrl_sdo = node.sdo[CANopenNode.H1F51_PROGRAM_CTRL][1]
    flash_sdo = node.sdo[CANopenNode.H1F57_FLASH_STATUS][1]

    node.nmt.state = "PRE-OPERATIONAL"
    time.sleep(0.5)

    ctrl_sdo.raw = PROGRAM_CTRL_STOP
    ctrl_sdo.raw = PROGRAM_CTRL_CLEAR

    print("flashing!")
    status = wait_flash_status_ok(flash_sdo, STATUS_TIMEOUT_S)

    if status != 0:
        pytest.fail(f"CLEAR call to flash failed with status 0x{status:08X}")

    with open(BIN_PATH, "rb") as infile:
        outfile = data_sdo.open(
            "wb",
            buffering=DOWNLOAD_BUFFER_SIZE,
            size=size,
            block_transfer=block_transfer,
            request_crc_support=request_crc,
        )
        outfile.write(infile.read())
        outfile.close()
    status = wait_flash_status_ok(flash_sdo, STATUS_TIMEOUT_S)

    if request_crc:
        print("requested CRC check")

    if status != 0:
        pytest.fail(f"FLASH failed with status 0x{status:08X}")

    ctrl_sdo.raw = PROGRAM_CTRL_START
    node.nmt.wait_for_bootup(timeout=BOOTUP_TIMEOUT_S)

    if confirm_image:
        node.nmt.state = "PRE-OPERATIONAL"
        time.sleep(0.5)
        ctrl_sdo.raw = PROGRAM_CTRL_ZEPHYR_CONFIRM
        print("requested image confirm")

    print("FLASH SUCCESSFUL!!!!!")
