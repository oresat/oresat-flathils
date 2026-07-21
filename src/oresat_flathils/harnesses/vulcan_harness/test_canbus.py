import time
import canopen
import pytest

H1F56_PROGRAM_SWID = 0x1F56


def test_canopen_heartbeat_received(canbus_device):
    """Test that the CANopen node sends a heartbeat message."""
    received_heartbeat = []

    def on_heartbeat(state):
        received_heartbeat.append(state)

    canbus_device.node.nmt.add_heartbeat_callback(on_heartbeat)

    time.sleep(3)  # allow a couple heartbeat cycles, CANopen is a bit slow
    assert len(received_heartbeat) > 0, "No heartbeat messages received"


def test_canopen_sdo_swid_read(canbus_device):
    """Program Software ID should be readable and non-null."""
    value = canbus_device.node.sdo[H1F56_PROGRAM_SWID][1].raw
    assert value is not None


def test_canopen_sdo_swid_write_rejected(canbus_device):
    """Program Software ID is read-only; writes should abort."""
    with pytest.raises(canopen.SdoAbortedError):
        canbus_device.node.sdo[H1F56_PROGRAM_SWID][1].raw = 0x12345678