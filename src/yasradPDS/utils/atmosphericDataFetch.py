#
# Nomads API https://docs.nomad-lab.eu/howto/manage/program/download.html
# Data can be acsessed here https://nomads.ncep.noaa.gov/ 
#Info on rocketpy's requriements from netCDF4 can be found here https://docs.rocketpy.org/en/latest/notebooks/environment/environment_analysis_EuroC_example.html 


"""
https://nomads.ncep.noaa.gov/info.php?page=opendap_grib_migration - Since NOMAD is depreciating OpenDAP acsess, wed need to use the Grib Filter
and then convert to NetCDF for rocketpy 
https://nomads.ncep.noaa.gov/gribfilter.php?ds=gefs_atmos_0p50a - GFS Ensemble Forecasts 
https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p50a.pl?dir=%2Fgefs.20261118%2F18%2Fatmos%2Fpgrb2ap5&file=geavg.t18z.pgrb2a.0p50.f000&all_var=on&all_lev=on 
Alternatively we could use siphon 
https://www.unidata.ucar.edu/software/tds
https://unidata.github.io/siphon/latest/ 

Or we could add uncertainties to forecast data 
"""
#https://docs.rocketpy.org/en/latest/notebooks/monte_carlo_analysis/monte_carlo_analysis.html 


from urllib import request
from netCDF4 import Dataset
from datetime import datetime, timezone, timedelta



import cfgrib
import requests





def fetch_ensemble_data(date : datetime, lattitude : float, longitude : float) -> Dataset:
    """Based on date, time, lattitude and longitude, return a netCDF4 ensemble in an appropriate formant for rocketpy usage"""
    ds = xr.open_dataset('era5-levels-members.grib', engine='cfgrib')

    
    
    
    
    
    return ds
import xarray as xr


def _download_grib_GEFS_Ensemble(date: datetime) -> list[str]:
    """Returns URLs leading to NOAA GEFS 0.5° Ensemble data."""

    # Concatenate in form base + ensemble_member
    time = datetime.now(timezone.utc) - timedelta(hours=5)

    # Ensure date is UTC-aware
    if date.tzinfo is None:
        date = date.replace(tzinfo=timezone.utc)

    # Determines which cycle of the day we use
    cycle_hour = (time.hour // 6) * 6
    cycle_time = time.replace(
        hour=cycle_hour, minute=0, second=0, microsecond=0
    )

    # If the cycle has not yet been initialized, use previous cycle
    # (normally unnecessary, but retained for safety)
    if cycle_time > time:
        cycle_time -= timedelta(hours=6)
    
    cycle = f"t{cycle_hour:02d}z"
    cycle2 = f"{cycle_hour:02d}"
    # Constant parts of the download URL
    part1 = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p50a.pl?dir=%2Fgefs."
    part2 = f"%2F{cycle2}%2Fatmos%2Fpgrb2ap5&file="
    part3 = ".pgrb2a.0p50."
    part4 = "&var_HGT=on&var_TMP=on&var_UGRD=on&var_VGRD=on&all_lev=on"

    # The day
    date_part = cycle_time.strftime("%Y%m%d")

    # Forecast
    delta = date - cycle_time
    hourDelta = int(round(delta.total_seconds() / 3600 / 3) * 3)
    hourDelta = max(0, hourDelta)

    forecast = f"f{hourDelta:03d}"

    # Download all ensemble members
    urls = []

    for i in range(1, 31):
        ensemble_member = f"gep{i:02d}"
        url = part1 + date_part + part2 + ensemble_member + "." + cycle + part3 + forecast + part4
        print(url)

#ds = cfgrib.open_datasets(webf[0], backend_kwargs={"indexpath": ""})

day = datetime(2026, 11, 18, 12, tzinfo=timezone.utc)
_download_grib_GEFS_Ensemble(day)