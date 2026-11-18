# rocketpy monte carlo dispersion analysis
import datetime

from rocketpy import Environment, Flight, Function, MonteCarlo, Rocket, SolidMotor

from rocketpy.stochastic import (
    StochasticEnvironment,
    StochasticFlight,
    StochasticNoseCone,
    StochasticParachute,
    StochasticRailButtons,
    StochasticRocket,
    StochasticSolidMotor,
    StochasticTail,
    StochasticTrapezoidalFins,
)

"""

https://nomads.ncep.noaa.gov/info.php?page=opendap_grib_migration - Since NOMAD is depreciating OpenDAP acsess, wed need to use the Grib Filter
"""
#https://docs.rocketpy.org/en/latest/notebooks/monte_carlo_analysis/monte_carlo_analysis.html 
#



