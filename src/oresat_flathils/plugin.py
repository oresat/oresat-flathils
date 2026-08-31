"""OreSat FlatHILS pytest plugin: harness selection and shared CLI options."""

import tomllib
from pathlib import Path

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """All CLI arguments."""
    group = parser.getgroup("flathils")
    group.addoption(
        "--test",
        default=None,
        help="Name of the harness to load from pyproject.toml.",
    )

    group.addoption(
        "--run-hil",
        action="store_true",
        default=False,
        help="Run Hardware-in-the-Loop (HIL) tests alongside isolated software tests.",
    )

    # CAN / Bootloader args
    group.addoption("--can-device", default=None, help="CAN device to use for HIL testing.")

    # Bootloader args
    group.addoption(
        "--confirm-image",
        action="store_true",
        default=False,
        help="Confirm the new image after a successful boot instead of leaving it pending.",
    )
    group.addoption(
        "--request-crc",
        action="store_true",
        default=False,
        help="Request a CRC check of the image before finalizing the transfer.",
    )
    group.addoption(
        "--throttle-delay",
        default=0,
        help="Delay in milliseconds between transfer chunks, to throttle bandwidth.",
    )
    group.addoption("--image-path", default=None, help="Path to the firmware image file to flash.")


def _get_harness_config(harness_name: str) -> dict[str, str]:
    """Fetch harness configuration from project config."""
    with Path("pyproject.toml").open("rb") as f:
        config = tomllib.load(f)
    harnesses = config.get("tool", {}).get("oresat_flathils", {}).get("harnesses", {})
    if harness_name not in harnesses:
        raise pytest.UsageError(f"Harness '{harness_name}' not found in pyproject.toml")
    return dict[str, str](harnesses[harness_name])


def _harness_dir(config: pytest.Config) -> Path | None:
    """Get harness directory from pyproject."""
    harness = config.getoption("--test")
    if not harness:
        return None
    harness_dir = _get_harness_config(harness).get("harness_dir")
    return Path(harness_dir).resolve() if harness_dir else None


def pytest_configure(config: pytest.Config) -> None:
    """Get Pytest configurations."""
    harness_dir = _harness_dir(config)
    if harness_dir is None:
        return

    env_path = harness_dir / "env.yaml"
    if env_path.exists() and env_path.stat().st_size > 0:
        config.option.lg_env = str(env_path)


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """When --harness is set, only run tests that live inside that harness's directory."""
    harness_dir = _harness_dir(config)
    if harness_dir is None:
        return

    keep, deselected = [], []
    for item in items:
        resolved = item.path.resolve()
        if resolved == harness_dir or harness_dir in resolved.parents:
            keep.append(item)
        else:
            deselected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
    items[:] = keep
