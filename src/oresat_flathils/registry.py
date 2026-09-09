"""Registry for FlatHILS CLI."""

from dataclasses import dataclass, field
from importlib.metadata import entry_points
from typing import Any


@dataclass
class CliHarnessArg:
    """Get CLI args."""

    flags: tuple[str, ...]
    dest: str
    required_for_hil_test: bool = False
    kwargs: dict[str, Any] = field(default_factory=dict)


@dataclass
class Harness:
    """Get which harness we're using."""

    name: str
    test_path: str
    args: list[CliHarnessArg] = field(default_factory=list)


def load_registry() -> dict[str, Harness]:
    """Load args registry."""
    return {ep.name: ep.load()() for ep in entry_points(group="flathils.harnesses")}
