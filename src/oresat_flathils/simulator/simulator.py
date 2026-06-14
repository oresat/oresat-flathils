"""OreSat FlatHILS Simulator Core Module.

Provides a BasiliskSimulator facade for encapsulating the Basilisk Simulation Framework.
"""

import logging
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    import types
    from collections.abc import Callable

from Basilisk.utilities import SimulationBaseClass, macros

log = logging.getLogger("simulator.core")


class BasiliskSimulator:
    """Wrapper for Basilisk (facade).

    This class abstracts Basilisk's underlying SimulationBaseClass.

    Docs: https://avslab.github.io/basilisk/Documentation/utilities/SimulationBaseClass.html
    """

    def __init__(self, mode: str = "isolated") -> None:
        """Initialize the simulator.

        Args:
            mode: "isolated" for pure software runs, or "integrated" for HIL runs.
        """
        self.mode = mode
        self._is_running = False
        self._callbacks: dict[str, list[Callable[[Any], None]]] = {}

        # Initialize core Basilisk simulation object
        self._sim = SimulationBaseClass.SimBaseClass()
        self._process_name = "OresatSimProc"
        self._task_name = "OresatSimTask"
        self._tick_rate_ns = macros.sec2nano(0.1)
        self._setup_base_processes()

        log.info("Initialized BasiliskSimulator in '%s' mode.", self.mode)

    def _setup_base_processes(self) -> None:
        """Configure baseline Basilisk processes and tasks.

        Docs: https://avslab.github.io/basilisk/Learn/bskPrinciples/bskPrinciples-1.html
        """
        self._proc = self._sim.CreateNewProcess(self._process_name)
        self._proc.addTask(self._sim.CreateNewTask(self._task_name, self._tick_rate_ns))

    def start(self) -> None:
        """Initialize the simulation.

        Docs: https://avslab.github.io/basilisk/Documentation/utilities/SimulationBaseClass.html
        """
        log.debug("Initializing Basilisk simulation state ...")
        self._sim.InitializeSimulation()
        self._is_running = True

    def step(self, duration_seconds: float) -> None:
        """Advance the simulation by some amount of time.

        Args:
            duration_seconds: Amount of time to step forward (in seconds).
        """
        if not self._is_running:
            raise RuntimeError("Simulation must be started before stepping.")

        stop_time_ns = self._sim.TotalSim.CurrentNanos + macros.sec2nano(duration_seconds)
        self._sim.ConfigureStopTime(stop_time_ns)
        self._sim.ExecuteSimulation()

    def stop(self) -> None:
        """Safely halt the simulation and clean up."""
        if self._is_running:
            log.debug("Halting simulation ...")
            self._is_running = False

    def __enter__(self) -> Self:
        """Context manager entry."""
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        """Context manager exit for safe teardown."""
        self.stop()
