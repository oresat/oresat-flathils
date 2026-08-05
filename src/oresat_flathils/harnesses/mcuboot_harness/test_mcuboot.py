import os
import time
from pathlib import Path

import canopen
import pytest

DOWNLOAD_BUFFER_SIZE = 889
STATUS_TIMEOUT_S = 30.0
BOOTUP_TIMEOUT_S = 20.0
SDO_TIMEOUT_S = 3.0
SDO_RETRIES = 3
CONFIRM_IMAGE = False
REQUEST_CRC = False

H1F50_PROGRAM_DATA = 0x1F50
H1F51_PROGRAM_CTRL = 0x1F51
H1F57_FLASH_STATUS = 0x1F57

PROGRAM_CTRL_STOP = 0x00
PROGRAM_CTRL_START = 0x01
PROGRAM_CTRL_CLEAR = 0x03
PROGRAM_CTRL_ZEPHYR_CONFIRM = 0x80

THROTTLE_DELAY = 0.0000095
CHANNEL = "can0"
BITRATE = 1_000_000
NODE_ID = 0x7C
BIN_PATH = Path(__file__).parent / "zephyr_image" / "zephyr.signed.bin"

@pytest.fixture(scope="session")
def block_transfer(pytestconfig):
    return pytestconfig.getoption("--use-block-transfer")

def create_object_dictionary():
    objdict = canopen.objectdictionary.ObjectDictionary()

    arr = canopen.objectdictionary.Array("Program data", H1F50_PROGRAM_DATA)
    var = canopen.objectdictionary.Variable("", H1F50_PROGRAM_DATA, subindex=1)
    var.data_type = canopen.objectdictionary.DOMAIN
    arr.add_member(var)
    objdict.add_object(arr)

    arr = canopen.objectdictionary.Array("Program control", H1F51_PROGRAM_CTRL)
    var = canopen.objectdictionary.Variable("", H1F51_PROGRAM_CTRL, subindex=1)
    var.data_type = canopen.objectdictionary.UNSIGNED8
    arr.add_member(var)
    objdict.add_object(arr)

    arr = canopen.objectdictionary.Array("Flash status", H1F57_FLASH_STATUS)
    var = canopen.objectdictionary.Variable("", H1F57_FLASH_STATUS, subindex=1)
    var.data_type = canopen.objectdictionary.UNSIGNED32
    arr.add_member(var)
    objdict.add_object(arr)

    return objdict


def wait_flash_status_ok(flash_sdo, timeout_s):
    end = time.time() + timeout_s
    status = int(flash_sdo.raw)

    while status != 0 and time.time() < end:
        time.sleep(0.1)
        status = int(flash_sdo.raw)

    return status


def test_mcuboot_flash_device(canbus_device: canopen.RemoteNode, block_transfer) -> None:
    """Flash a built zephyr image with CANopen"""

    if not BIN_PATH.is_file():
        pytest.fail(f"No binary file found on: {BIN_PATH}")

    size = os.path.getsize(BIN_PATH)

    node = canbus_device.network.add_node(NODE_ID, create_object_dictionary())

    if block_transfer:
        print(f"\nUsing Block transfer at a delay of {THROTTLE_DELAY} sec...")
        original_send = node.network.bus.send

        def throttle_send(msg, timeout=None):
            original_send(msg, timeout)
            time.sleep(THROTTLE_DELAY)

        node.network.bus.send = throttle_send

    node.sdo.MAX_RETRIES = SDO_RETRIES
    node.sdo.RESPONSE_TIMEOUT = SDO_TIMEOUT_S

    data_sdo = node.sdo[H1F50_PROGRAM_DATA][1]
    ctrl_sdo = node.sdo[H1F51_PROGRAM_CTRL][1]
    flash_sdo = node.sdo[H1F57_FLASH_STATUS][1]


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
            request_crc_support=REQUEST_CRC,
        )
        outfile.write(infile.read())
        outfile.close()
    status = wait_flash_status_ok(flash_sdo, STATUS_TIMEOUT_S)

    if status != 0:
        pytest.fail(f"FLASH failed with status 0x{status:08X}")

    ctrl_sdo.raw = PROGRAM_CTRL_START
    node.nmt.wait_for_bootup(timeout=BOOTUP_TIMEOUT_S)

    if CONFIRM_IMAGE:
        node.nmt.state = "PRE-OPERATIONAL"
        time.sleep(0.5)
        ctrl_sdo.raw = PROGRAM_CTRL_ZEPHYR_CONFIRM

    print("FLASH SUCCESSFUL!!!!!")
