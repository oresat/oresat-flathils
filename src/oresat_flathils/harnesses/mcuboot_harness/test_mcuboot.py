from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from flash_canopen import flash_device

if TYPE_CHECKING:
    from oresat_flathils.hardware.hardware import CANBus

H1F56_PROGRAM_SWID = 0x1F56

BIN_PATH = Path(__file__).parent / "zephyr_image" / "zephyr.signed.bin"


def test_canopen_flash_success(canbus_device: CANBus) -> None:
    """First, flash a zephyr image, CANopen should test everything else."""
    assert canbus_device.node is not None

    result = flash_device(
        channel="can0",
        node_id=0x7C,
        bin_path=BIN_PATH,
    )

    assert result == 0, f"Zephyr flash was unsuccessful (status code {result})."
