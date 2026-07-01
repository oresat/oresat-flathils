"""OreSat FlatHILS Core Module Test Runner."""

import logging

from oresat_flathils.simulator.simulator import BasiliskSimulator

log = logging.getLogger("sim_only")


def run_sim_only() -> int:
    """Simulation-only entrypoint."""
    # make this an argument in the future
    logging.basicConfig(level=logging.INFO)
    log.info("Set logging level to INFO.")

    log.info("Building simulation.")

    bsk_sim = BasiliskSimulator(mode="isolated")

    # start adding features to simulation
    bsk_sim.build_sim()

    # run simulation
    log.info("Preparing to run simulation")
    log.warning("Running the simulation has not been implemented, finishing.")

    return 0
