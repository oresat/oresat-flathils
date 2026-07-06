"""Pytest fixtures for the Simulator Integration."""

import logging
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from collections.abc import Generator

from .simulator import BasiliskSimulator

log = logging.getLogger("simulator.fixtures")


@pytest.fixture
def flathils_sim(request: pytest.FixtureRequest) -> Generator[BasiliskSimulator]:
    """Provide a BasiliskSimulator instance for test cases.

    This fixture ensures that the simulator is safely initialized and torn down.
    """
    run_hil = request.config.getoption("--run-hil", default=False)
    mode = "integrated" if run_hil else "isolated"

    log.info("Setting up BasiliskSimulator in '%s' mode...", mode)

    sim = BasiliskSimulator(mode=mode)
    sim.start()

    yield sim

    log.info("Tearing down BasiliskSimulator...")
    sim.stop()
