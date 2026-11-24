# rocketpy assisted descent calculations (altitude/velocity-time sims) 

import math
from datetime import date, timedelta, datetime
from rocketpy import Environment, PointMassRocket, Flight, Rocket
from yasradPDS.systems.system import System
from yasradPDS.utils.atmosphere import LaunchSite, forecast, standard
from yasradPDS.geometries.geometry import Geometry
from matplotlib import pyplot as plt


import numpy as np

#For the assumption that the rocket is a point mass, Radius only needs to be non zero for the analysis to run and the rest don't matter
ROCKET_MAX_RADIUS : float = 1 #m
ROCKET_BURN_CD = 0 
ROCKET_OFF_CD = 0
COM_NO_MOTOR = 0 #Distance from rocket coordinate system orgin

#For a pure descent test, these are ignored, but still needed to create descent objects
RAIL_LENGTH : float = 1 # RocketPy doesn't accept <= 0 for rail_length
RAIL_INCLINATION : float = 0


#Apogee, Where the rocket descends from
APOGEE = 10000
#For a pure descent from apogee



def descent_analysis(sys : System, site : LaunchSite, date : datetime, atmosphere : str = "standard"):
    """
    Returns a rocketpy flight object for the system dropped from apogee containing all descent kinematics data.
    
    Note: RocketPy does consider the coriolis effect so a slight horizontal drift is expected
    
    Default atmosphere is "standard".
    
    CSV export lives in export/csv_data.py (run via `export csv` in the CLI).
    """

    
    descent = get_descent_flight_3_DOF(sys=sys, site=site, date=date, atmosphere=atmosphere)
    descent.plots.trajectory_3d()


    #Grabbing descent data for both matplotlib and csv export 
    timeAltitude = np.array(descent.z)
    timeVelocity = np.array(descent.vz)
    timeAccel = np.array(descent.az)

    #Plotting the alt, v, and a vertically stacked
    fig, z = plt.subplots(3, 1)
    

    
    z[0].set_title("Altitude after apogee until impact")
    z[0].set_ylabel("Altitude ASL (m)")
    z[0].set_xlabel("Time After Apogee (s)")
    z[0].plot(timeAltitude[:, 0], timeAltitude[:, 1])
    z[0].axhline(descent.env.elevation, color="red", linewidth=0.8, linestyle="--")  # ground; forecast replaces site.elevation with GFS terrain

    z[1].set_title("Vertical velocity after apogee until impact")
    z[1].set_ylabel("Z - Velocity (m/s, down +ve)")
    z[1].set_xlabel("Time After Apogee (s)")
    z[1].plot(timeVelocity[:, 0], -timeVelocity[:, 1])  # negate vz -> downward reads positive
    z[1].axhline(0, color="red", linewidth=0.8, linestyle="--")  # 0 m/s reference (apogee)

    z[2].set_title("Vertical acceleration after apogee until impact")
    z[2].set_ylabel("Z - Acceleration (m/s^2)")
    z[2].set_xlabel("Time After Apogee (s)")
    z[2].plot(timeAccel[:, 0], timeAccel[:, 1])
    plt.subplots_adjust(hspace=0.6, wspace=0.6)
    plt.show()



def get_descent_flight_3_DOF(sys : System, site : LaunchSite, date : datetime, atmosphere : str = "standard") -> Flight:
    """
    Returns a rocketpy flight object for the system dropped from apogee containing all descent kinematics data.

    Note: RocketPy does consider the coriolis effect so a slight Eastward drift is expected if winds are zero
    """
    #Get Mass of rocket
    mass = 0
    
    #Makes the assumption that the first chute of any deployment system opens at apogee
    apogee = sys.get(0, "deploy_altitude")

    for i in range(1):
        mass += sys.get(i, "total_mass")

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

    env : Environment = forecast(site, date) if atmosphere == "forecast" else standard(site)
    #initial_solution for Flight simulation, we simulate the rocket as if it is not in motion at apogee. Everything 
    initial_state : list = [
    0, #Initial Time
    0, 0, apogee, #x, y, z
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


