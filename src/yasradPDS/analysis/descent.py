# rocketpy assisted descent calculations (altitude/velocity-time sims) 

import math
from datetime import datetime
from rocketpy import Environment, PointMassRocket, Flight, Rocket
from systems.system import System
from utils.atmosphere import LaunchSite, forecast


#For the assumption that the rocket is a point mass, Radius can be anything and the rest are all 0
ROCKET_MAX_RADIUS : float = 0 #m
ROCKET_BURN_CD = 0 
ROCKET_OFF_CD = 0
COM_NO_MOTOR = 0 #Distance from rocket coordinate system orgin




#For a pure descent test, these are ignored
RAIL_LENGTH : float = 0
RAIL_INCLINATION : float = 0


#Apogee
APOGEE = 10000

#For a pure descent from apogee




def get_descent_3_DOF(sys : System, launch_site : LaunchSite, date : datetime) -> Flight:
    """
    Returns a rocketpy flight object for the system dropped from apogee containing all descent kinematics data.
    """
    #Get Mass of rocket
    mass = 0
    for i in range(1):

        mass += sys.get(i, "mass_lower") + sys.get(i, "mass_upper")


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


        ####Check to see if im doing this right, as im acsessing private variables and doing thing
        cd_s = sys._stage_list[i].CD * radius**2 * (math.pi)
        ####

        trigger_altitude = sys.get(i, "deploy_altitude")
        fill_time = sys.get(i, "fill_time")
        rocket.add_parachute(name=chute_name, cd_s = cd_s, trigger=trigger_altitude, radius=radius, lag= fill_time)

    env : Environment = forecast(launch_site=launch_site, date=date)

    initial_state : list = [
    0, #Initial Time
    0, 0, APOGEE, #x, y, z
    0, 0, 0, #Velocity Components
    1, 0, 0, 0, #Quaternion Rotations
    0, 0, 0 #Angular velocities
]

    descent : Flight = Flight(
        rocket=rocket,
        rail_length= RAIL_LENGTH,
        environment=env,
        initial_solution=initial_state,
        simulation_mode="3 DOF"
    )
    return descent




"""Testing stuff ########################"""
env = Environment(latitude=32.990254, longitude=-106.974998, elevation=1400)

tomorrow = datetime.date.today() + datetime.timedelta(days=1)
env.set_date(
    (tomorrow.year, tomorrow.month, tomorrow.day, 12)
)  # Hour given in UTC time
#Define rocket
rocket : PointMassRocket = PointMassRocket(
        radius = ROCKET_MAX_RADIUS,
        mass= 35,
        center_of_mass_without_motor=COM_NO_MOTOR,
        power_off_drag=ROCKET_OFF_CD,
        power_on_drag=ROCKET_BURN_CD
    )

rocket.add_parachute(
    name="Main",
    cd_s=10.0,
    trigger=800)

rocket.add_parachute(
    name="drogue",
    cd_s = 1.0,
    trigger = "apogee"
)
#In meters
expected_apogee = env.elevation + 9144

#Pass into simulation object, 14 element vector
apogee = [
    0, 
    0, 0, expected_apogee,
    0, 0, 0,
    1, 0, 0, 0,
    0, 0, 0
]

descent : Flight = Flight(
    rocket=rocket,
    environment=env,
    initial_solution=apogee,
    rail_length=1,
    simulation_mode= "3 DOF",
    max_time=600
)
descent.plots.trajectory_3d()
descent.plots.linear_kinematics_data()