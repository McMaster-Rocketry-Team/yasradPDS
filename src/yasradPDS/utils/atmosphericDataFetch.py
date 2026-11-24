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
    """
    Returns a list URLs leading to each ensemble member's NOAA GEFS 0.5° Ensemble data. 
    Currently does not allow for past weather data/Data beyond 14 days of the present

    Date - Day of launch. Num ensembles - the number of ensembles desireed, max 31

    """

    #Look for NOMADS data from 5 hours earlier to prevent searching for nonexisting data
    init_time = datetime.now().astimezone(timezone.utc) - timedelta(hours=5)

    # Convert datetime to UTC time

    date = date.astimezone(timezone.utc)
    if(date - init_time > timedelta(hours = 360)):
        raise ValueError("date must be within the next 14 days of current UTC time, otherwise ensemble data does not exist")
    if(date - init_time < datetime.today().astimezone(timezone.utc)):
        raise ValueError("Getting past forecast data is currently unsupported")
    if(num_ensembles > 31):
        raise ValueError("NOAA GEFS 0.5° only has 31 Ensemble Members")
    if(num_ensembles < 1):
        raise ValueError("Must request at least 1 ensemble")

    


    

    # Determines which cycle of the day we use - Publishes new data at 0:00, 6:00, 12:00, 18:00 UTC
    cycle_hour = (init_time.hour // 6) * 6

    #The cycle dataset that is to be used based on when this function was called
    init_cycle_time = init_time.replace(
        hour=cycle_hour, minute=0, second=0, microsecond=0
    )
    

    #Cycle hours (from 0:00 utc every 6 hours), things just to create the correct url for the desired dataset
    cycle = f"t{cycle_hour:02d}z"
    cycle2 = f"{cycle_hour:02d}"

    # Url parts that dont really change, probably should rename parts to more meaningful variable names
    part1 = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p50a.pl?dir=%2Fgefs."
    part2 = f"%2F{cycle2}%2Fatmos%2Fpgrb2ap5&file="
    part3 = ".pgrb2a.0p50."

    #The data that we want, rocketpy only needs HGT
    values = "&var_HGT=on&var_TMP=on&var_UGRD=on&var_VGRD=on&all_lev=on"

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
                + part3 + forecast + values
            )

            urls.append(url)

    return urls


def add_ensembles_to_env(env : Environment):
    """
    Appends ensemble data to the specified enviroment

    
    """
    urls = _get_grib_GEFS_Ensemble_URLs(env.date, 3)

    files = []
    #This will take a while
    for i in range(len(urls)):

        #Downloads the Grib files
        path, http = request.urlretrieve(urls[i])

        #A Delay between requests is requested by NOMAD
        sleep(2)
        files.append(path)
        print(path)
    #Need to add file cleanup, as current files are stored in a temp folder location
    
    ensembles = []
    #This bit needs to be completed
    for i in files:
        ds : xr.Dataset = cfgrib.open_datasets(i, backend_kwargs={"indexpath": ""})
        ensembles.append(ds)

    Environment

def _xrDataset_to_rocketPyNetCDF4(ensemble_datasets : xr.Dataset, lat : float, lon : float) -> netCDF4.Dataset:
    pass
