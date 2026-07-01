"""OreSat FlatHILS Core Module Test Runner."""

import logging
import tomllib
from pathlib import Path
from typing import cast

from oresat_flathils.simulator.simulator import BasiliskSimulator

log = logging.getLogger("sim_only")


def run_sim_only() -> int:
    """Simulation-only entrypoint"""

    # make this an argument in the future
    logging.basicConfig(level = logging.INFO)
    log.info("Set logging level to INFO.")

    log.info("Building simulation.")

    bsk_sim = BasiliskSimulator(mode="isolated")

    # start adding features to simulation
    bsk_sim.build_sim()

    # run simulation
    log.info("Preparing to run simulation")
    log.warning("Running the simulation has not been implemented, finishing.")

    return 0



# at some point, there will need to be an equivalent for retrieving simulation information
#def _get_harness_config(harness_name: str) -> dict[str, str]:
#    """Fetch harness configuration from project config."""
#    with Path("pyproject.toml").open("rb") as f:
#        config = tomllib.load(f)
#
#    harnesses = config.get("tool", {}).get("oresat_flathils", {}).get("harnesses", {})
#
#    if harness_name not in harnesses:
#        raise ValueError(f"Harness '{harness_name}' not found in pyproject.toml")
#
#    return cast("dict[str, str]", harnesses[harness_name])
