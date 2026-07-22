import time
from typing import TYPE_CHECKING

import canopen
import pytest

if TYPE_CHECKING:
    from oresat_flathils.hardware.hardware import CANBus

H1F56_PROGRAM_SWID = 0x1F56


def test_canopen_heartbeat_received(canbus_device: CANBus) -> None:
    """Test that the CANopen node sends a heartbeat message."""
    assert canbus_device.node is not None

    received_heartbeat = []

    def on_heartbeat(state: int) -> None:
        received_heartbeat.append(state)

    canbus_device.node.nmt.add_heartbeat_callback(on_heartbeat)

    time.sleep(3)  # allow a couple heartbeat cycles, CANopen is a bit slow
    assert len(received_heartbeat) > 0, "No heartbeat messages received"


def test_canopen_sdo_swid_read(canbus_device: CANBus) -> None:
    """Program Software ID should be readable and non-null."""
    assert canbus_device.node is not None

    value = canbus_device.node.sdo[H1F56_PROGRAM_SWID][1].raw
    assert value is not None


def test_canopen_sdo_swid_write_rejected(canbus_device: CANBus) -> None:
    """Program Software ID is read-only; writes should abort with the correct code."""
    assert canbus_device.node is not None

    with pytest.raises(canopen.SdoAbortedError) as exc_info:
        canbus_device.node.sdo[H1F56_PROGRAM_SWID][1].raw = 0x12345678

    assert exc_info.value.code == 0x06010002, (
        f"Expected read-only abort (0x06010002), got {exc_info.value.code:#010x}"
    )
