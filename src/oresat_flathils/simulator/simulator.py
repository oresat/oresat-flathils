"""OreSat FlatHILS Simulator Core Module.

Provides a BasiliskSimulator facade for encapsulating the Basilisk Simulation Framework.
"""

import logging
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    import types
    from collections.abc import Callable

import numpy as np
from Basilisk.utilities import SimulationBaseClass, macros, unitTestSupport
from Basilisk.simulation import spacecraft

from Basilisk.utilities import simIncludeGravBody # gravity

from Basilisk.simulation import magneticFieldWMM # magnetic field
from Basilisk.architecture import astroConstants # not sure, maybe for sun

from Basilisk.simulation import eclipse # energy analysis
from Basilisk.simulation import simpleBattery # energy analysis
from Basilisk.simulation import simpleSolarPanel # energy analysis
from Basilisk.simulation import simplePowerSink # energy analysis

from Basilisk.utilities.supportDataTools.dataFetcher import get_path, DataFile

log = logging.getLogger("simulator.core")

# this may not be needed
#import os
#path = os.path.dirname(os.path.abspath(filename))
#bskPath = __path__[0]

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
        # For example, there can be one just for orbial and rigid body dynamics, and one just for flight sofware.
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
        """Adds features to simulation

        Ideally, a satellite static config and orbital config would be passed.
        """
        # epoch message for WMM reference
        self._epochMsg = unitTestSupport.timeStringToGregorianUTCMsg('2025 June 27, 10:23:0.0 (UTC)')
        # initial time when simulation is to start
        self._timeInitString = "2026-02-10T20:00:00Z"
        # spice objects (earth, sun) must be created before spacecraft is added

        # SATELLITE PARAMETERS
        satellite_name = "example-satelllite"
        mass  = 3.5 # kg, 
        # rotational inertia placeholder
        # should be part of the satellite's static configuration
        Jxx = 0.01650237
        Jxy = 0.00000711
        Jxz = 0.00004547
        Jyx = Jxy
        Jyy = 0.015962
        Jyz = 0.00003107
        Jzx = Jxz
        Jzy = Jyz
        Jzz = 0.00651814
        rot_I = np.array([[Jxx, Jxy, Jxz], [Jyx, Jyy, Jyz], [Jzx, Jzy, Jzz]])

        # ORBITAL PARAMETERS
        # initial MRP attitude placeholder, may be non-zero
        sigma = np.array([0.0, 0.0, 0.0])
        # rotational speed placeholder
        # should be part of the satellite's orbital configuration
        omega = np.array([-0.15707963, -0.0418879,  -0.07330383])

        # example for 2025 Jun 27, 10:23:0.0 (UTC)
        # this could be calculated from the orbital elements
        # so the config should be able to accept this or
        # the orbital elements
        position = np.array([ 175981.01262138, 1412067.83525838, 6812565.32607667])
        velocity = np.array([ 4940.03683994, -5636.92201438,  1051.77468059])


        # CREATE THE SATELLITE
        log.info("Creating spacecraft.")
        scObject = spacecraft.Spacecraft()
        scObject.ModelTag = satellite_name
        scObject.hub.mHub = mass
        scObject.hub.IHubPntBc_B = rot_I
        scObject.hub.sigma_BNInit = sigma 
        scObject.hub.omega_BN_BInit = omega

        # note, these probably have to be set AFTER
        # generating the gravityFactory / spice object
        # or else the coordinate system may be off,
        # please double check
        scObject.hub.r_CN_NInit = position
        scObject.hub.r_CN_NInit = velocity


        log.info("Done creating spacecraft.")
        # temporary variables for commonly used attributes
        # a message is used to pass infomation between models
        scObjectMsg = scObject.scStateOutMsg
        # a recorder is made to store data from the simulation
        scObjectRec = scObjectMsg.recorder()

        log.info(f"Adding spacecraft to task \"{self._task_name}\".")
        # both the spacecraft and the recorder are added as a task in the sim
        # note this is for a dynamics based task
        self._sim.AddModelToTask(self._task_name, scObject)
        # add the recoder to the task to have it save data
        self._sim.AddModelToTask(self._task_name, scObjectRec)



        # CREATE THE SYSTEM
        # every orbital simulation needs a gravity body
        gravFactory = simIncludeGravBody.gravBodyFactory()
        earth = gravFactory.createEarth()
        earth.isCentralBody = True
        
        # you can also create the sun, but that is not needed if there
        # are no solar simulations
        sun = gravFactory.createSun()

        # Unsure of it is important when to add spacecraft
        gravFactory.addBodiesTo(scObject)


        # CREATE SYSTEM AS SPICE OBJECT (sun is an option)
        # create the spice objects, must create earth and sun first
        spiceObject = gravFactory.createSpiceInterface(time=self._timeInitString, epochInMsg=True)
        # data should automatically be loaded 
        # spiceObject = gravFactory.createSpiceInterface(time=self._init_timestring, epochInMsg=True)
        spiceObject.addPlanetNames(["earth"])
        spiceObject.zeroBase = "earth"

        earthMsg = spiceObject.planetStateOutMsgs[0]
        earthRec = earthMsg.recorder()
        sunMsg = spiceObject.planetStateOutMsgs[0]
        sunRec = sunMsg.recorder()

        # have the earth in the gravity factory
        # follow the earth in the spice object
        # not sure if this is needed
        earth.planetBodyInMsg.subscribeTo(earthMsg)
        #gravFactory.gravBodies.get("earth").planetBodyInMsg.subscribeTo(spiceObject.planetStateOutMsgs[0])

        log.info(f"Adding spice object to task \"{self._task_name}\".")
        # Add models and (optional) recorders to simulation
        # the last argument is priority, higher means higher priority
        self._sim.AddModelToTask(self._task_name, spiceObject, -1)
        self._sim.AddModelToTask(self._task_name, earthRec)
        self._sim.AddModelToTask(self._task_name, sunRec)



        # CREATE THE MAGNETIC FIELD (option)
        # add a magnetic field if needed
        magModel= magneticFieldWMM.MagneticFieldWMM()
        magModel.ModelTag = "magModel" # I think this could be anything, such as "WMM"
        # this model uses data that is packaged with Basilisk
        magModel.configureWMMFile(str(get_path(DataFile.MagneticFieldData.WMM)))
 
        # Add the satellite to the model
        magModel.addSpacecraftToModel(scObject.scStateOutMsg)  # this command can be repeated if multiple
       
        magMsg = magModel.envOutMsgs[0]
        magRec = magMsg.recorder()

        # Add model and (optional) recorder to simulation
        log.info(f"Adding World Magnetic Model task \"{self._task_name}\".")
        self._sim.AddModelToTask(self._task_name, magModel)
        self._sim.AddModelToTask(self._task_name, magRec)



        # IMPLEMENT EARTH ECLIPSE (option)
        # Implement earth eclipsing the sun, if needed
        # check if there should be lunar eclipsing too
        eclipseModel = eclipse.Eclipse()
        eclipseModel.ModelTag = "eclipseModel"

        # add satellite, earth, and sun to model
        eclipseModel.addSpacecraftToModel(scObjectMsg)
        eclipseModel.addPlanetToModel(earthMsg)
        eclipseModel.sunInMsg.subscribeTo(sunMsg)

        eclipseMsg = eclipseModel.eclipseOutMsgs[0]
        eclipseRec = eclipseMsg.recorder()

        # add model and (optional) recorder to task
        log.info(f"Adding eclipse model to task \"{self._task_name}\".")
        self._sim.AddModelToTask(self._task_name, eclipseModel)
        self._sim.AddModelToTask(self._task_name, eclipseRec)


        # OPTIONAL SECTION: POWER

        # ADD SOLAR PANELS (option)
        # ideally, loop through a config and add all solar panels, if enabled

        # nHat_B: normal vector relative to spacecraft body
        # panelArea: panel area (m^2)
        # panelEfficiency: nondimensional efficiency, typically [0.1, 0,5]
        solar_panel_parameters = {"nHat_B": np.array([1, 0, 0]),
                                  "panelArea": 0.2*0.3,
                                  "panelEfficiency": 0.20} 

        # this function can be called multiple times in a loop if needed
        solar_panel_1 = self._get_solar_panel("solarPanel1", 
                                            scObject=scObject, 
                                            eclipseMsg=eclipseMsg, 
                                            sunMsg=sunMsg, 
                                            parameters=solar_panel_parameters)

        solar_panel_1_Msg = solar_panel_1.nodePowerOutMsg
        solar_panel_1_Rec = solar_panel_1_Msg.recorder()
        log.info(f"Adding solar panel to task \"{self._task_name}\".")
        self._sim.AddModelToTask(self._task_name, solar_panel_1)
        self._sim.AddModelToTask(self._task_name, solar_panel_1_Rec)
       

        # ADD POWER SINKS (option)
        # ideally, loop through a config and add all power sinks, if enabled
        # simple power sinks can only be turned on and off and have a constant load
        # depending on the config, these might be passed to the flight software
        power_sink_1 = simplePowerSink.SimplePowerSink()
        power_sink_1.ModelTag = "powerSink1"
        power_sink_1.nodePowerOut = -3.  # Watts, placeholder value, add to config
        
        power_sink_1_Msg = power_sink_1.nodePowerOutMsg
        power_sink_1_Rec = power_sink_1_Msg.recorder()
        log.info(f"Adding power sink to task \"{self._task_name}\".")
        self._sim.AddModelToTask(self._task_name, power_sink_1)
        self._sim.AddModelToTask(self._task_name, power_sink_1_Rec)


        # ADD POWER MONITOR
        # maybe condense all batteries into one battery for simplicity
        powerMonitor = simpleBattery.SimpleBattery()
        powerMonitor.ModelTag = "battery1Model"
        powerMonitor.storageCapacity = (10.0*3600.0)
        powerMonitor.storedCharge_Init = (10.0*3600.0)

        powerMonitor.addPowerNodeToModel(solar_panel_1_Msg)
        powerMonitor.addPowerNodeToModel(power_sink_1_Msg)
        powerMonitorRec = powerMonitor.batPowerOutMsg.recorder()
        log.info(f"Adding power monitor (battery) to task \"{self._task_name}\".")
        self._sim.AddModelToTask(self._task_name, powerMonitor)
        self._sim.AddModelToTask(self._task_name, powerMonitorRec)




    def _get_solar_panel(self, modelTag, scObject, eclipseMsg, sunMsg, parameters):
        '''
        Parameters
            modelTag: name for model
            scObject: satellite
            eclipseMsg: eclipse messages
            sunMsg: sun messages
            parameters: additional parameters in kwarg dictionary form

        returns
            solarPanel: simpleSolarPanel()
        '''
        solarPanel = simpleSolarPanel.SimpleSolarPanel()
        solarPanel.ModelTag = modelTag
        solarPanel.stateInMsg.subscribeTo(scObject.scStateOutMsg)
        solarPanel.sunEclipseInMsg.subscribeTo(eclipseMsg)
        solarPanel.sunInMsg.subscribeTo(sunMsg)
        solarPanel.setPanelParameters(**parameters)

        return solarPanel


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
