# rocketpy assisted descent calculations (altitude/velocity-time sims) 

import math
from datetime import date, timedelta, datetime
from rocketpy import Environment, PointMassRocket, Flight, Rocket
from yasradPDS.systems.system import System
from yasradPDS.utils.atmosphere import LaunchSite, forecast, standard
from yasradPDS.geometries.geometry import Geometry
from yasradPDS.config.defaults import FILE_PATH
from matplotlib import pyplot as plt


import numpy as np

#For the assumption that the rocket is a point mass, Radius only needs to be non zero for the analysis to run and the rest don't matter
ROCKET_MAX_RADIUS : float = 1 #m
ROCKET_BURN_CD = 0 
ROCKET_OFF_CD = 0
COM_NO_MOTOR = 0 #Distance from rocket coordinate system orgin

#For a pure descent test, these are ignored, but still needed to create descent objects
RAIL_LENGTH : float = 0
RAIL_INCLINATION : float = 0


#Apogee, Where the rocket descends from
APOGEE = 10000
#For a pure descent from apogee



def descent_analysis(sys : System, site : LaunchSite, date : datetime, file_name : str | None = None):
    """
    Returns a rocketpy flight object for the system dropped from apogee containing all descent kinematics data.
    
    Note: RocketPy does consider the coriolis effect so a slight horizontal drift is expected
    
    If a file name is provided, a CSV file containing all data will be saved to FILE_PATH configured in defaults.py
    """
    
    
    descent = get_descent_flight_3_DOF(sys=sys, site=site, date=date)
    descent.plots.trajectory_3d()


    #Grabbing descent data for both matplotlib and csv export 
    timeAltitdue = np.array(descent.z)
    timeVelocity = np.array(descent.vz)
    timeAccel = np.array(descent.az)

    #Plotting the alt, v, and a vertically stacked
    fig, z = plt.subplots(3, 1)
    
    altitudeHeader = ["Time (s)", "Altitude ASL (m)"]
    z[0].set_title("Altitude after apogee until impact")
    z[0].set_ylabel("Altitude ASL (m)")
    z[0].set_xlabel("Time After Apogee (s)")
    z[0].plot(timeAltitdue[:, 0], timeAltitdue[:, 1])

    velocityHeader = ["Time (s)", "Vertical Velocity"]
    z[1].set_title("Vertical velocity after apogee until impact")
    z[1].set_ylabel("Z - Velocity (m/s)")
    z[1].set_xlabel("Time After Apogee (s)")
    z[1].plot(timeVelocity[:, 0], timeVelocity[:, 1])
    z[1].yaxis.set_inverted(True)

    accelHeader = ["Time (s)", "Vertical Accel"]
    z[2].set_title("Vertical acceleration after apogee until impact")
    z[2].set_ylabel("Z - Acceleration (m/s^2)")
    z[2].set_xlabel("Time After Apogee (s)")
    z[2].plot(timeAccel[:, 0], timeAccel[:, 1])
    plt.subplots_adjust(hspace=0.6, wspace=0.6)
    plt.show()

    
    if file_name is not None:
        vertStack = np.vstack((altitudeHeader, timeAltitdue, velocityHeader, timeVelocity, accelHeader, timeVelocity))
        file = open(file=str(FILE_PATH + "/" + file_name +".csv"), mode="w")
        for i in vertStack:
            file.write(",".join(map(str, i)) + "\n")
        file.close()


def get_descent_flight_3_DOF(sys : System, site : LaunchSite, date : datetime) -> Flight:
    """
    Returns a rocketpy flight object for the system dropped from apogee containing all descent kinematics data.

    Note: RocketPy does consider the coriolis effect so a slight Eastward drift is expected
    """
    #Get Mass of rocket
    mass = 0
    for i in range(1):

        mass += sys.get(i, "mass_lower") + sys.get(i, "mass_upper")

    print(f"mass of rocket is {mass} kg")

    #Create rocket
    rocket : PointMassRocket = PointMassRocket(
        radius = ROCKET_MAX_RADIUS,
        mass= mass,
        center_of_mass_without_motor=COM_NO_MOTOR,
        power_off_drag=ROCKET_OFF_CD,
        power_on_drag=ROCKET_BURN_CD
    )


    #Add chutes
    for i in range(sys.stage_count):
        chute_name = sys.get(i, "name")
        radius = sys.get(i, "main_diameter")/2
        cd_s = sys.get(i, "CD") * sys.get(i, "area")
        trigger_altitude = sys.get(i, "deploy_altitude")
        fill_time = sys.get(i, "fill_time")
        rocket.add_parachute(name=chute_name, cd_s = cd_s, trigger=trigger_altitude, radius=radius, lag= fill_time)

    env : Environment = standard(launch_site=site, date=date)

    #initial_solution for Flight simulation, we simulate the rocket as if it is not in motion at apogee. Everything 
    initial_state : list = [
    0, #Initial Time
    0, 0, APOGEE, #x, y, z
    0, 0, 0, #Velocity Components
    1, 0, 0, 0, #Quaternion Rotations - Irrelevant for 3dof
    0, 0, 0 #Angular velocities - Irrelevant for 3dof
]

    descent : Flight = Flight(
        rocket=rocket,
        rail_length= RAIL_LENGTH,
        environment=env,
        initial_solution=initial_state,
        simulation_mode="3 DOF",
        max_time_step= 1,
        max_time=600
    )
    return descent


sampleSystem = System()

