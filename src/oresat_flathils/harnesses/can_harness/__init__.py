"""CAN harness registration."""

from pathlib import Path

from oresat_flathils.registry import CliHarnessArg, Harness


def get_spec() -> Harness:
    """Arguments used for CAN Harness."""
    return Harness(
        name="can-harness",
        test_path=str(Path(__file__).parent),
        args=[
            CliHarnessArg(
                flags=("--can-device",),
                dest="can_device",
                required_for_hil_test=True,
                kwargs={"default": None, "help": "CAN device to use for HIL testing."},
            ),
        ],
    )
