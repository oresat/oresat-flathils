import odrive
from odrive.utils import dump_errors, run_state
from odrive.utils import high_rate_capture, high_rate_capture_start, TimestampFmt
from odrive.enums import AxisState

import time
import numpy as np
import scipy as sp
from enum import Enum

import matplotlib.pyplot as plt
# create enums

# create typed dict for test steps (input and recording)

tests = {
    "stage_0": {
        "desc": "Set the velocity to zero and collect data.",
        "fixture": {
            "desc": "Set velocity to zero",
            "vel_ramp_rate": 10.0,
            "input_vel": 0.0,
        },
        "recordings": {
            "record_1": {
                "desc": "Record at zero velocity.",
                "trigger_velocity": 0,
                "trigger_deadband": 0.1,
                "trigger_delay": 3,
            },
        },
    },
    "stage_1": {
        "desc": "Record power draws while ramping up to 100 rev/s",
        "fixture": {
            "desc": "Ramp up to 100 rev/s",
            "vel_ramp_rate": 20.0,
            "input_vel": 100.0,
        },
        "recordings": {
            "record_2": {
                "desc": "Record power draw at ramping",
                "trigger_velocity": 50,
                "trigger_deadband": 2,
                "trigger_delay": 0.0,
            },
            "record_3": {
                "desc": "Record power draw at idle steady state",
                "trigger_velocity": 100,
                "trigger_deadband": 1,
                "trigger_delay": 10.0,
            },
        },
    },
}


high_rate_capture_params = {
    "odrv": None, 
    "properties": [
        'axis0.vel_estimate', 
        'axis0.motor.fet_thermistor.temperature', 
        'ibus', 
        'vbus_voltage'
    ],
    "return_as": np.recarray,
    "t_fmt": TimestampFmt.NANOSECONDS
}


def postprocess_data(data):
    """Creates data for test report"""
    velocity_mean = np.mean(data['axis0.vel_estimate'])
    acceleration = np.gradient(data['axis0.vel_estimate']) / np.gradient(data['timestamps'])
    acceleration_mean = np.mean(acceleration)

    power_data = data['ibus'] * data['vbus_voltage']
    power_mean = np.mean(power_data)
    power_clusters, _ = sp.cluster.vq.kmeans(power_data, 2)
    power_clusters = np.sort(power_clusters)

    velocity_slope = (sp.stats.linregress(data['timestamps'], data['axis0.vel_estimate'])).slope

    return velocity_mean, velocity_slope, acceleration, acceleration_mean, power_data, power_mean, power_clusters


if __name__ == "__main__":
    # Find the odrive
    print("Finding an odrive...")
    odrv0 = odrive.find_any()
    print("Found Odrive!")

    high_rate_capture_params["odrv"] = odrv0

    # calibrate
    print("\nStarting motor calibration...")
    run_state(odrv0.axis0, AxisState.MOTOR_CALIBRATION)
    print("Motor calibration complete.")
    print("Starting encoder calibration...")
    run_state(odrv0.axis0, AxisState.ENCODER_OFFSET_CALIBRATION)
    print("Encoder offset calibration complete.")

    datasets = []
    dataset_dict = {}

    # Enter closed loop control
    print("\nPutting odrive in CLOSED_LOOP_CONTROL state...")
    odrv0.axis0.requested_state = AxisState.CLOSED_LOOP_CONTROL

    for stage_name, stage in tests.items():
        print(f"\nStarting new stage {stage_name}...")

        dataset_dict[stage_name] = {}

        # set up the fixture
        fixture = stage["fixture"]
        print(f"Setting ramp rate to {fixture['vel_ramp_rate']}")
        odrv0.axis0.controller.config.vel_ramp_rate = fixture["vel_ramp_rate"]
        print(f"Setting velocity to {fixture['input_vel']}")
        odrv0.axis0.controller.input_vel = fixture["input_vel"]
        print("Stage setup complete")

        # Go through each recording request
        recordings = stage['recordings']
        for rec_name, rec_params in recordings.items():
            print(f"\nStarting new recording step {rec_name}...")
            print(f"Waiting for motor to be within {rec_params['trigger_deadband']} of  {rec_params['trigger_velocity']} rev/s...")
            # do a check, if the waiting state is not between the current state 
            while (abs(odrv0.axis0.vel_estimate - rec_params["trigger_velocity"]) > rec_params["trigger_deadband"]):
                time.sleep(0.01)
                # TODO: do a check, if the waiting state is not 
                # between the current state and 
                # the target state, throw an error
            print("Recoding triggered")
            if rec_params['trigger_delay'] > 0.0:
                print(f"Delaying data collection by {rec_params['trigger_delay']} seconds...")
                time.sleep(rec_params['trigger_delay'])
            print("Recording data...")
            data = high_rate_capture(**high_rate_capture_params)
            datasets.append(data)
            dataset_dict[stage_name][rec_name] = data
            print("Data collected")


    # return to idle state
    print("\nReturning odrive to IDLE state...")
    odrv0.axis0.requested_state = AxisState.IDLE
    show_plots = False

    if show_plots:
        _, _, accel_1, _, odrive_power_1, mean_1, clusters_1 = postprocess_data(datasets[1])
        _, _, accel_2, _, odrive_power_2, mean_2, clusters_2 = postprocess_data(datasets[2])


        fig, ax = plt.subplots(2, 7)

        # ramping power graph
        ax[0, 0].plot(datasets[1]['timestamps'], odrive_power_1)
        ax[0, 0].set_title("Calculated power")
        # ax[0, 1].plot(datasets[1]['timestamps'], datasets[1]['ibus'])
        ax[0, 1].hist(datasets[1]['ibus'], bins=50)
        ax[0, 1].set_title("ibus current")
        # ax[0, 2].plot(datasets[1]['timestamps'], datasets[1]['vbus_voltage'])
        ax[0, 2].hist(datasets[1]['vbus_voltage'], bins=50)
        ax[0, 2].set_title("vbus volage")
     
        # ramping power histogram
        ax[0, 3].hist(odrive_power_1, bins=50)
        ax[0, 3].set_xlim(-6, 18)
       
        ax[0, 4].plot(datasets[1]['timestamps'], datasets[1]['axis0.motor.fet_thermistor.temperature'])
        ax[0, 4].set_ylim(60, 140)

        ax[0, 5].plot(datasets[1]['timestamps'], accel_1)
        ax[0, 6].plot(datasets[1]['timestamps'], datasets[1]['axis0.vel_estimate'])



        # steady state power graph
        ax[1, 0].plot(datasets[2]['timestamps'], odrive_power_2)

        # ax[1, 1].plot(datasets[2]['timestamps'], datasets[2]['ibus'])
        ax[1, 1].hist(datasets[2]['ibus'], bins=50)
        ax[1, 1].set_title("ibus current")
        # ax[1, 2].plot(datasets[2]['timestamps'], datasets[2]['vbus_voltage'])
        ax[1, 2].hist(datasets[2]['vbus_voltage'], bins=50)
        ax[1, 2].set_title("vbus volage")
     
     
        # steady state power histogram
        ax[1, 3].hist(odrive_power_2, bins=50)
        ax[1, 3].set_xlim(-6, 18)
        for val in clusters_2:
            ax[1, 3].axvline(val)

        ax[1, 4].plot(datasets[2]['timestamps'], datasets[2]['axis0.motor.fet_thermistor.temperature'])
        ax[1, 4].set_ylim(70, 130)

        ax[1, 5].plot(datasets[2]['timestamps'], accel_2)
        ax[1, 6].plot(datasets[2]['timestamps'], datasets[2]['axis0.vel_estimate'])

        plt.show()


    # save report output
    with open("report.txt", 'w') as fd:
        report_strings = []
        for ii, data in enumerate(datasets):

            velocity_mean = np.mean(data['axis0.vel_estimate'])
            acceleration = np.gradient(data['axis0.vel_estimate']) / np.gradient(data['timestamps'])
            acceleration_mean = np.mean(acceleration)

            ibus_current_mean = np.mean(data['ibus'])
            ibus_current_clusters, _ = sp.cluster.vq.kmeans(data['ibus'], 2)
            ibus_current_clusters = np.sort(ibus_current_clusters)

            vbus_voltage_mean = np.mean(data['vbus_voltage'])
            vbus_voltage_clusters, _ = sp.cluster.vq.kmeans(data['vbus_voltage'], 2)
            vbus_voltage_clusters = np.sort(vbus_voltage_clusters)

            power_data = data['ibus'] * data['vbus_voltage']
            power_mean = np.mean(power_data)
            power_clusters, _ = sp.cluster.vq.kmeans(power_data, 2)
            power_clusters = np.sort(power_clusters)

            velocity_slope = (sp.stats.linregress(data['timestamps'], data['axis0.vel_estimate'])).slope

            report_string = ""
            report_string += f"[TEST_{ii}]\n"
            report_string += f"velocity_mean = {velocity_mean}\n"
            report_string += f"velocity_slope = {velocity_slope}\n"
            report_string += f"acceleration_mean = {acceleration_mean}\n"
            report_string += f"ibus_current_mean = {ibus_current_mean}\n"
            report_string += f"ibus_current_clusters = {ibus_current_clusters.tolist()}\n"
            report_string += f"vbus_voltage_mean = {vbus_voltage_mean}\n"
            report_string += f"vbus_voltage_clusters = {vbus_voltage_clusters.tolist()}\n"
            report_string += f"bus_power_mean = {power_mean}\n"
            report_string += f"power_clusters = {power_clusters.tolist()}\n"
            report_strings.append(report_string)

        fd.write("\n".join(report_strings))
        print("\n".join(report_strings))

    # save data to csv
    for ii,dataset in enumerate(datasets):
        np.savetxt(f"data_{ii}.csv", dataset, delimiter=",")


    plt.show()
