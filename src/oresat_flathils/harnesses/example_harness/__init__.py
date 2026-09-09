"""Example harness registration."""

from pathlib import Path

from oresat_flathils.registry import Harness


def get_spec() -> Harness:
    """Arguments used for Example Harness."""
    return Harness(
        name="example-harness",
        test_path=str(Path(__file__).parent),
        args=[],
    )
