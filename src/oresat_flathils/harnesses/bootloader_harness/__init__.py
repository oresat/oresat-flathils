"""Bootloader harness registration."""

from pathlib import Path

from oresat_flathils.registry import CliHarnessArg, Harness


def get_spec() -> Harness:
    """Arguments used for Bootloader Harness."""
    return Harness(
        name="bootloader-harness",
        test_path=str(Path(__file__).parent),
        args=[
            CliHarnessArg(
                flags=("--can-device",),
                dest="can_device",
                required_for_hil_test=True,
                kwargs={"default": None, "help": "CAN device to use for HIL testing."},
            ),
            CliHarnessArg(
                flags=("--image-path",),
                dest="image_path",
                required_for_hil_test=True,
                kwargs={"default": None, "help": "Path to the firmware image file to flash."},
            ),
            CliHarnessArg(
                flags=("--confirm-image",),
                dest="confirm_image",
                kwargs={
                    "action": "store_true",
                    "default": False,
                    "help": "Confirm the new image after a successful boot.",
                },
            ),
            CliHarnessArg(
                flags=("--request-crc",),
                dest="request_crc",
                kwargs={
                    "action": "store_true",
                    "default": False,
                    "help": "Request a CRC check of the image before finalizing the transfer.",
                },
            ),
            CliHarnessArg(
                flags=("--throttle-delay",),
                dest="throttle_delay",
                kwargs={
                    "type": float,
                    "default": 0,
                    "help": "Delay in seconds between transfer chunks, to throttle bandwidth.",
                },
            ),
        ],
    )
