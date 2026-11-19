# rocketpy monte carlo dispersion analysis
import datetime

from rocketpy import Environment, Flight, Function, MonteCarlo, Rocket, SolidMotor
import siphon 
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
and then convert to NetCDF for rocketpy 
https://nomads.ncep.noaa.gov/gribfilter.php?ds=gefs_atmos_0p50a - GFS Ensemble Forecasts 
- Need to get UGRD, VGRD, PRES, and VVEL Parameters
- - Sample URL https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p50a.pl?dir=%2Fgefs.20261118%2F18%2Fatmos%2Fpgrb2ap5&file=geavg.t18z.pgrb2a.0p50.f000&all_var=on&all_lev=on 

Alternatively we could use siphon 
https://www.unidata.ucar.edu/software/tds
https://unidata.github.io/siphon/latest/ 

Or we could add uncertainties to forecast data 
"""
#https://docs.rocketpy.org/en/latest/notebooks/monte_carlo_analysis/monte_carlo_analysis.html 






