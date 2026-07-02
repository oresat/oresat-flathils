"""OreSat FlatHILS Simulator Core Module.

Provides a BasiliskSimulator facade for encapsulating the Basilisk Simulation Framework.
"""

import logging
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    import types
    from collections.abc import Callable


import numpy as np
from Basilisk.simulation import (
    eclipse,  # energy analysis
    magneticFieldWMM,  # magnetic field
    simpleBattery,  # energy analysis
    simplePowerSink,  # energy analysis
    simpleSolarPanel,  # energy analysis
    spacecraft,
)
from Basilisk.utilities import (
    SimulationBaseClass,
    macros,
    simIncludeGravBody,  # gravity
    unitTestSupport,
)
from Basilisk.utilities.supportDataTools.dataFetcher import DataFile, get_path

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

        # Add a process. There can be multiple processes for each simulation.
        # For example, there can be one just for orbial and rigid body dynamics,
        # and one just for flight sofware.
        self._process_name = "OresatSimProc"

        # Every process will be added as a task
        self._task_name = "OresatSimTask"

        # Each task can have its own update rate, and they do not have to be the same
        self._tick_rate_ns = macros.sec2nano(0.1)

        self._setup_base_processes()

        log.info("Initialized BasiliskSimulator in '%s' mode.", self.mode)

    def _setup_base_processes(self) -> None:
        """Configure baseline Basilisk processes and tasks.

        Docs: https://avslab.github.io/basilisk/Learn/bskPrinciples/bskPrinciples-1.html
        """
        self._proc = self._sim.CreateNewProcess(self._process_name)
        self._proc.addTask(self._sim.CreateNewTask(self._task_name, self._tick_rate_ns))

    def build_sim(self) -> None:
        """Build simulation.

        Ideally, a satellite static config and orbital config would be passed.
        """
        # epoch message for WMM reference
        self._epochMsg = unitTestSupport.timeStringToGregorianUTCMsg(
            '2025 June 27, 10:23:0.0 (UTC)'
        )
        # initial time when simulation is to start
        self._timeInitString = "2026-02-10T20:00:00Z"
        # spice objects (earth, sun) must be created before spacecraft is added

        self._msgs = {}
        self._recs = {}

        # SATELLITE PARAMETERS
        satellite_name = "example-satelllite"
        mass = 3.5  # kg
        # rotational inertia placeholder
        # should be part of the satellite's static configuration
        jxx = 0.01650237
        jxy = 0.00000711
        jxz = 0.00004547
        jyx = jxy
        jyy = 0.015962
        jyz = 0.00003107
        jzx = jxz
        jzy = jyz
        jzz = 0.00651814
        rot_inertia = np.array([[jxx, jxy, jxz], [jyx, jyy, jyz], [jzx, jzy, jzz]])

        # ORBITAL PARAMETERS
        # initial MRP attitude placeholder, may be non-zero
        sigma = np.array([0.0, 0.0, 0.0])
        # rotational speed placeholder
        # should be part of the satellite's orbital configuration
        omega = np.array([-0.15707963, -0.0418879, -0.07330383])

        # example for 2025 Jun 27, 10:23:0.0 (UTC)
        # this could be calculated from the orbital elements
        # so the config should be able to accept this or
        # the orbital elements
        position = np.array([175981.01262138, 1412067.83525838, 6812565.32607667])
        velocity = np.array([4940.03683994, -5636.92201438, 1051.77468059])

        # CREATE THE SATELLITE
        log.info("Creating spacecraft.")
        sc_object = spacecraft.Spacecraft()
        sc_object.ModelTag = satellite_name
        sc_object.hub.mHub = mass
        sc_object.hub.IHubPntBc_B = rot_inertia
        sc_object.hub.sigma_BNInit = sigma
        sc_object.hub.omega_BN_BInit = omega

        # note, these probably have to be set AFTER
        # generating the gravityFactory / spice object
        # or else the coordinate system may be off,
        # please double check
        sc_object.hub.r_CN_NInit = position
        sc_object.hub.r_CN_NInit = velocity

        log.info("Done creating spacecraft.")

        # temporary variables for commonly used attributes
        # a message is used to pass infomation between models
        sc_object_msg = sc_object.scStateOutMsg
        # a recorder is made to store data from the simulation
        sc_object_rec = sc_object_msg.recorder()

        self._msgs[satellite_name] = sc_object_msg
        self._recs[satellite_name] = sc_object_rec

        log.info("Adding spacecraft to task.")
        # both the spacecraft and the recorder are added as a task in the sim
        # note this is for a dynamics based task
        self._sim.AddModelToTask(self._task_name, sc_object)
        # add the recoder to the task to have it save data
        self._sim.AddModelToTask(self._task_name, sc_object_rec)

        # CREATE THE SYSTEM

        self._make_spice_object(
            sc_object=sc_object,
            earth_name="earthModel",
            sun_name="sunModel",  # if you don't want the sun, set this to None
            moon_name="moonModel",  # if you don't want the moon, set this to None
        )

        # MAKE MAGNETIC MODEL
        # maybe pass arguments if needed
        self._make_mag_model(name="magneticModel", sc_name=satellite_name)

        # MAKE ECLIPSE MODEL
        # maybe pass arguments if needed
        self._make_eclipse_model(
            name="eclipseModel",
            sc_name=satellite_name,
            earth_name="earthModel",
            sun_name="sunModel",
            moon_name="moonModel",
        )

        # OPTIONAL SECTION: POWER

        # ADD SOLAR PANELS (option)
        # ideally, loop through a config and add all solar panels, if enabled

        # nHat_B: normal vector relative to spacecraft body
        # panelArea: panel area (m^2)
        # panelEfficiency: nondimensional efficiency, typically [0.1, 0,5]
        solar_panel_parameters = {
            "nHat_B": np.array([1, 0, 0]),
            "panelArea": 0.2 * 0.3,
            "panelEfficiency": 0.20,
        }

        # this function can be called multiple times in a loop if needed
        self._make_solar_panel(
            name="solarPanel1",
            sc_name=satellite_name,
            sun_name="sunModel",
            eclipse_name="eclipseModel",
            parameters=solar_panel_parameters,
        )

        self._make_power_sink(
            name="powerSink1",
            node_power=-3.0,
        )

        self._make_power_monitor(
            name="battery1Model",
            initial_charge=10.0 * 3600.0,
            total_capacity=10.0 * 3600.0,
            node_names=["solarPanel1", "powerSink1"],
        )

    def _make_spice_object(
        self,
        sc_object: spacecraft.Spacecraft,
        earth_name: str,
        sun_name: str | None = None,
        moon_name: str | None = None,
    ) -> None:
        """Add gravity and create spice object.

        Optionally adds sun (for solar) and moon (for solar + gravity).
        """
        # CREATE THE SYSTEM
        # every orbital simulation needs a gravity body
        # gravity can be way more complicated:
        # https://avslab.github.io/basilisk/_modules/scenarioOrbitMultiBody.html#run
        # https://avslab.github.io/basilisk/_modules/simIncludeGravBody.html#gravBodyFactory
        # additionally, there is data that is packaged with Basilisk,
        # but it is not used here.
        grav_factory = simIncludeGravBody.gravBodyFactory()
        earth = grav_factory.createEarth()
        earth.isCentralBody = True

        # you can also create the sun, but that is not needed if there
        # are no solar simulations
        # apparently the sun is not used
        if sun_name is not None:
            log.info("Including sun in gravity and spice model.")
            # We don't acutally need to save what it returns
            _ = grav_factory.createSun()

        # you can also create the sun, but that is not needed if there
        # are no solar simulations
        # apparently the sun is not used
        if moon_name is not None:
            log.info("Including moon in gravity and spice model.")
            # We don't actually need to save what it returns
            _ = grav_factory.createMoon()

        # Unsure of it is important when to add spacecraft
        grav_factory.addBodiesTo(sc_object)

        # CREATE SYSTEM AS SPICE OBJECT (sun is an option)
        # create the spice objects, must create earth and sun first
        spice_object = grav_factory.createSpiceInterface(time=self._timeInitString, epochInMsg=True)
        # data should automatically be loaded
        spice_object.zeroBase = "earth"

        # the following is in the same order that they were created in gravity factory
        spice_body_count = 0

        earth_msg = spice_object.planetStateOutMsgs[spice_body_count]
        earth_rec = earth_msg.recorder()
        self._msgs[earth_name] = earth_msg
        self._recs[earth_name] = earth_rec
        spice_body_count += 1

        if sun_name is not None:
            sun_msg = spice_object.planetStateOutMsgs[spice_body_count]
            sun_rec = sun_msg.recorder()
            self._msgs[sun_name] = sun_msg
            self._recs[sun_name] = sun_rec
            spice_body_count += 1

        if moon_name is not None:
            moon_msg = spice_object.planetStateOutMsgs[spice_body_count]
            moon_rec = moon_msg.recorder()
            self._msgs[moon_name] = moon_msg
            self._recs[moon_name] = moon_rec
            spice_body_count += 1

        # have the earth in the gravity factory
        # follow the earth in the spice object
        # not sure if this is needed: earth.planetBodyInMsg.subscribeTo(earth_msg)

        log.info("Adding spice object to task.")
        # Add models and (optional) recorders to simulation
        # the last argument is priority, higher means higher priority
        self._sim.AddModelToTask(self._task_name, spice_object)
        self._sim.AddModelToTask(self._task_name, earth_rec)
        if sun_name is not None:
            self._sim.AddModelToTask(self._task_name, sun_rec)
        if moon_name is not None:
            self._sim.AddModelToTask(self._task_name, moon_rec)

    def _make_mag_model(self, name: str, sc_name: str) -> None:
        """Add world magnetic model to simulation."""
        mag_model = magneticFieldWMM.MagneticFieldWMM()
        mag_model.ModelTag = name
        # this model uses data that is packaged with Basilisk
        mag_model.configureWMMFile(str(get_path(DataFile.MagneticFieldData.WMM)))

        # Add the satellite to the model
        # this command can be repeated if multiple spacecraft are needed
        mag_model.addSpacecraftToModel(self._msgs[sc_name])

        mag_msg = mag_model.envOutMsgs[0]
        mag_rec = mag_msg.recorder()

        self._msgs[name] = mag_msg
        self._recs[name] = mag_rec

        # Add model and (optional) recorder to simulation
        log.info("Adding World Magnetic Model task.")
        self._sim.AddModelToTask(self._task_name, mag_model)
        self._sim.AddModelToTask(self._task_name, mag_rec)

    def _make_eclipse_model(
        self,
        name: str,
        sc_name: str,
        earth_name: str,
        sun_name: str,
        moon_name: str | None = None,
    ) -> None:
        """Make an eclipse model."""
        # IMPLEMENT EARTH ECLIPSE (option)
        # Implement earth eclipsing the sun, if needed
        # check if there should be lunar eclipsing too
        eclipse_model = eclipse.Eclipse()
        eclipse_model.ModelTag = name

        # add satellite, earth, and sun to model
        # reference self._msgs[name]
        eclipse_model.addSpacecraftToModel(self._msgs[sc_name])
        eclipse_model.addPlanetToModel(self._msgs[earth_name])
        eclipse_model.sunInMsg.subscribeTo(self._msgs[sun_name])
        # both sun and earth are required, but moon is optional
        if moon_name is not None:
            # You would need a special orbit to see if this works
            eclipse_model.addPlanetToModel(self._msgs[moon_name])

        eclipse_msg = eclipse_model.eclipseOutMsgs[0]
        eclipse_rec = eclipse_msg.recorder()

        # not sure if this will work
        self._msgs[name] = eclipse_msg
        self._recs[name] = eclipse_rec

        # add model and (optional) recorder to task
        log.info("Adding eclipse model to task")
        self._sim.AddModelToTask(self._task_name, eclipse_model)
        self._sim.AddModelToTask(self._task_name, eclipse_rec)

    def _make_solar_panel(
        self,
        name: str,
        sc_name: str,
        sun_name: str,
        eclipse_name: str,
        parameters: dict,  # type hint may require a protocol
    ) -> None:
        """Create a solar panel."""
        log.info("Building solar panel.")
        solar_panel = simpleSolarPanel.SimpleSolarPanel()
        solar_panel.ModelTag = name
        solar_panel.stateInMsg.subscribeTo(self._msgs[sc_name])
        solar_panel.sunInMsg.subscribeTo(self._msgs[sun_name])
        solar_panel.sunEclipseInMsg.subscribeTo(self._msgs[eclipse_name])
        solar_panel.setPanelParameters(**parameters)

        solar_panel_msg = solar_panel.nodePowerOutMsg
        solar_panel_rec = solar_panel_msg.recorder()

        self._msgs[name] = solar_panel_msg
        self._recs[name] = solar_panel_rec

        log.info("Adding solar panel to task.")
        self._sim.AddModelToTask(self._task_name, solar_panel)
        self._sim.AddModelToTask(self._task_name, solar_panel_rec)

    def _make_power_sink(self, name: str, node_power: float) -> None:
        """Build a power sink and add it to the simulation."""
        # ADD POWER SINKS (option)
        # ideally, loop through a config and add all power sinks, if enabled
        # simple power sinks can only be turned on and off and have a constant load
        # depending on the config, these might be passed to the flight software
        power_sink = simplePowerSink.SimplePowerSink()
        power_sink.ModelTag = name
        power_sink.nodePowerOut = node_power  # Watts, placeholder value, add to config

        power_sink_msg = power_sink.nodePowerOutMsg
        power_sink_rec = power_sink_msg.recorder()

        self._msgs[name] = power_sink_msg
        self._recs[name] = power_sink_rec

        log.info("Adding power sink to task.")
        self._sim.AddModelToTask(self._task_name, power_sink)
        self._sim.AddModelToTask(self._task_name, power_sink_rec)

    def _make_power_monitor(
        self,
        name: str,
        total_capacity: float,
        initial_charge: float,
        node_names: list[str],
    ) -> None:
        """Make power monitor."""
        # ADD POWER MONITOR
        # maybe condense all batteries into one battery for simplicity
        power_monitor = simpleBattery.SimpleBattery()
        power_monitor.ModelTag = name
        power_monitor.storageCapacity = total_capacity
        power_monitor.storedCharge_Init = initial_charge

        # loop through all power nodes to add
        for node_name in node_names:
            power_monitor.addPowerNodeToModel(self._msgs[node_name])

        power_monitor_msg = power_monitor.batPowerOutMsg
        power_monitor_rec = power_monitor_msg.recorder()

        self._msgs[name] = power_monitor_msg
        self._recs[name] = power_monitor_rec

        log.info("Adding power monitor (battery) to task.")
        self._sim.AddModelToTask(self._task_name, power_monitor)
        self._sim.AddModelToTask(self._task_name, power_monitor_rec)

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
