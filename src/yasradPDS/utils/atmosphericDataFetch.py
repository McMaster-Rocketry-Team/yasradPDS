#
# Nomads API https://docs.nomad-lab.eu/howto/manage/program/download.html
# Data can be acsessed here https://nomads.ncep.noaa.gov/ 
#Info on rocketpy's requriements from netCDF4 can be found here https://docs.rocketpy.org/en/latest/notebooks/environment/environment_analysis_EuroC_example.html 


"""
https://nomads.ncep.noaa.gov/info.php?page=opendap_grib_migration - Since NOMAD is depreciating OpenDAP acsess, wed need to use the Grib Filter
and then convert to NetCDF for rocketpy 
"""
#https://docs.rocketpy.org/en/latest/notebooks/monte_carlo_analysis/monte_carlo_analysis.html 
#https://docs.rocketpy.org/en/latest/user/environment/3-further/other_apis.html 
#https://docs.rocketpy.org/en/latest/_modules/rocketpy/environment/environment.html 
from urllib import request
from netCDF4 import Dataset
from datetime import datetime, timezone, timedelta
from rocketpy import Environment
import xarray as xr
import cfgrib
from time import sleep
import netCDF4
import numpy as np

def _get_grib_GEFS_Ensemble_URLs(date: datetime, num_ensembles : int):
    """Returns URLs leading to each ensemble member's NOAA GEFS 0.5° Ensemble data. If the requested forecast does n
    Date should be UTC time
    """

    #Go back 5 hrs to prevent acsessing unpublished NOMAD data
    init_time = datetime.now().astimezone(timezone.utc) - timedelta(hours=5)
    # Set date to UTC time
    date = date.astimezone(timezone.utc)
    if(date - init_time > timedelta(hours = 360)):
        raise ValueError("date must be within the next 14 days of current UTC time, otherwise ensemble data does not exist")


    


    

    # Determines which cycle of the day we use
    cycle_hour = (init_time.hour // 6) * 6
    init_cycle_time = init_time.replace(
        hour=cycle_hour, minute=0, second=0, microsecond=0
    )
    

    

    #Cycle hours (from 0:00 utc every 6 hours), also things just for the url link
    cycle = f"t{cycle_hour:02d}z"
    cycle2 = f"{cycle_hour:02d}"

    # Url parts taht dont really change
    part1 = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p50a.pl?dir=%2Fgefs."
    part2 = f"%2F{cycle2}%2Fatmos%2Fpgrb2ap5&file="
    part3 = ".pgrb2a.0p50."
    part4 = "&var_HGT=on&var_TMP=on&var_UGRD=on&var_VGRD=on&all_lev=on"

    # The day
    date_part = init_cycle_time.strftime("%Y%m%d")

    delta = date - init_cycle_time
    forecast_hours = delta.total_seconds() / 3600
    start_hour = int(round(forecast_hours / 3) * 3)

    # Generate more forecasts
    hours = range(start_hour, start_hour + 9, 3)

    urls = []

    for i in range(num_ensembles):

        ensemble_member = "gec00" if i == 0 else f"gep{i:02d}"

        for hour in hours:

            forecast = f"f{hour:03d}"

            url = (
                part1 + date_part + part2
                + ensemble_member + "." + cycle
                + part3 + forecast + part4
            )

            urls.append(url)

    return urls


def add_ensembles_to_env(env : Environment):
    """Appends ensemble data to the specified enviroment"""
    urls = _get_grib_GEFS_Ensemble_URLs(env.date, 3)

    files = []
    #This will take a while
    for i in range(len(urls)):
        path, http = request.urlretrieve(urls[i])
        sleep(2)
        files.append(path)
        print(path)

    ensembles = []
    #This bit needs to be completed
    for i in files:
        ds : xr.Dataset = cfgrib.open_datasets(i, backend_kwargs={"indexpath": ""})
        ensembles.append(ds)

    Environment

def _xrDataset_to_rocketPyNetCDF4(ensemble_datasets : xr.Dataset, lat : float, lon : float) -> netCDF4.Dataset:
    pass
