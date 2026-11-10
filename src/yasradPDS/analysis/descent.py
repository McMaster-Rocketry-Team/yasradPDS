# rocketpy assisted descent calculations (altitude/velocity-time sims) 


#Return Altitude Time graph

from rocketpy import Environment
from rocketpy import Rocket
from rocketpy import Flight
from ..utils import atmosphere as atm
from ..config import defaults


#Set this to enviroment later
env : Environment

#Define rocket
rocket : Rocket = Rocket(
    #Radius
    #Mass 
    #Moment of Inertia Tuple
    #Cd2 - No motor so no need to consider exhaust pressure
    #Cd1
    #Center of mass without motor
    #Coordinate SYstem Orientation
)

#Add parachutes to rocket
rocket.add_parachute(
    #Name = "Main"
    #Drag coefficient multiplied by area
    #Trigger (Altitude in m, Apogee, etc)
    #Sampling Rate (Frequency of checks)

)

#In meters
expected_apogee = 9144

#Pass into simulation object, 14 element vector
apogee = [
    0, 
    0, expected_apogee, 0,
    0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0
]

descent : Flight = Flight(
    rocket=rocket,
    environment=enviroment,
    initial_solution=apogee
)
descent.plots.trajectory_3d()
descent.plots.linear_kinematics_data()