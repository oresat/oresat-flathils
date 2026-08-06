import time
from typing import TYPE_CHECKING

import canopen
import pytest

if TYPE_CHECKING:
    import can

H1F56_PROGRAM_SWID = 0x1F56


def test_canopen_heartbeat_received(bootloader_node: canopen.RemoteNode) -> None:
    """Test that the CANopen node sends a heartbeat message."""
    received_heartbeat = []

    def on_heartbeat(state: int) -> None:
        received_heartbeat.append(state)

    bootloader_node.nmt.add_heartbeat_callback(on_heartbeat)

    time.sleep(3)  # allow a couple heartbeat cycles, CANopen is a bit slow
    assert len(received_heartbeat) > 0, "No heartbeat messages received"


def test_canopen_sdo_swid_read(bootloader_node: canopen.RemoteNode) -> None:
    """Program Software ID should be readable as a valid, non-zero UNSIGNED32."""
    value = bootloader_node.sdo[H1F56_PROGRAM_SWID][1].raw

    assert isinstance(value, int)
    assert 0 < value <= 0xFFFFFFFF, f"SWID out of UNSIGNED32 range: {value:#010x}"


def test_canopen_sdo_swid_write_rejected(bootloader_node: canopen.RemoteNode) -> None:
    """Program Software ID is read-only; writes should abort with the correct code."""
    with pytest.raises(canopen.SdoAbortedError) as exc_info:
        bootloader_node.sdo[H1F56_PROGRAM_SWID][1].raw = 0x12345678

    assert exc_info.value.code == 0x06010002, (
        f"Expected read-only abort (0x06010002), got {exc_info.value.code:#010x}"
    )


def test_can_interface_raw_frame(canbus: can.BusABC) -> None:
    """Sanity check that raw CAN frames can be received on the bus."""
    msg = canbus.recv(timeout=3)
    assert msg is not None, "No CAN frames received on bus"
