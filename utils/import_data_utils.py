"""
    Hydrometric Import Data Utilities

    This module provides functions to retrieve, process, and store hydrometric data from 
    public APIs and web scraping sources. It includes utilities for querying station metadata, 
    downloading water level data, and saving results in various formats (CSV, Parquet).

    Functions:
    ----------
    - get_station_id_basin_map: Retrieves a mapping of station IDs to their names and basins 
      from a given API endpoint.

    - fetch_hydrometr_data: Downloads daily hydrometric observations for a given station and date.

    - save_daily_data: Saves a day's worth of water level data to a local file (CSV or Parquet).

    - fetch_hidmet: (DOESN'T WORK) Scrapes water stage (in cm) from the Hidmet Serbian national meteorological 
      website and returns it as a DataFrame.

    Author: Lorenzo Cane - DBL E&E Area Consultant  
    Last modified: 20/06/2025
"""


import requests
from io import StringIO
import os
import pandas as pd
import xarray as xr

def get_station_id_basin_map(url, placeholder_id = 237, option = 1):
    '''
        Fetch data from the given url API, returns a mapping of station IDs to station basin and station name.

        Parameters:
        -----------
        url : str
            The base URL of the API endpoint (.php).
        placeholder_id : int, optional
            ID of a known station to use in the request (default is 237).
        option : int, optional
            Option parameter for the API (default is 1).

        Returns:
        --------
        dict
            A dictionary mapping station IDs (str) to dictionaries with 'name' and 'basin' keys.

    '''
    #Compose complete url
    url = url + "?" + "id_station=" + str(placeholder_id) + "&option=" + str(option)
    #print(f'Fetching data from: {url}')
    #Try to get API from the given station
    try:
        resp = requests.get(url)
        #Give feedback on query requests
        resp.raise_for_status()
        #Save data into json
        data = resp.json()
        #Save ahs infos into dict
        station_list = data.get("ahs_list", [])
        output_dict = { entry["id"]: {
                                      "name": entry["name"],
                                      "basin": entry["basin"]
                                    }
                            for entry in station_list            
                        }

        return output_dict 

    #Deal with request exception:
    except requests.RequestException as e:
        print(f'Error fetchin station data: {e} \nTry with another placeholder_id')
        return {}
    #Deal with parsing error
    except ValueError as e:
        print(f'Error while parsing JSON data of station {placeholder_id}: {e} \nTry with a different placeholder_id')

def fetch_hydrometr_data(url, station_id, date):
    '''
        Fetches daily hydrometric measurements for a specific station and date.

        Parameters:
        -----------
        url : str
            Base URL of the API endpoint.
        station_id : str or int
            The station ID to query.
        date : datetime
            The date for which data is requested.

        Returns:
        --------
        dict
            Parsed JSON response from the API containing measurement data.

        Raises:
        -------
        HTTPError
            If the HTTP request fails.
    '''
    #Complete url
    url = url + "?" + "id_station=" + str(station_id) +"&sdate=" + date.strftime("%Y-%m-%d")
    print(url)
    #params dict as named in the php
    params = {"id_station": station_id, "sdate": date.strftime("%Y-%m-%d")}
    #request response after API request
    resp = requests.get(url, params=params)
    #HTTP error check
    resp.raise_for_status()

    print(f'Data request from station {station_id} fetched and loaded into JSON file')
    return resp.json()
    

def save_daily_data(data, station_id, date, data_dir, 
                    format= "csv"):
    '''
        Saves daily hydrometric data to disk in the specified format (CSV or Parquet).

        Parameters:
        -----------
        data : dict
            JSON response containing hydrometric data.
        station_id : str or int
            Station ID used for naming the file.
        date : datetime
            Date of the dataset, used for naming the file.
        data_dir : str
            Directory where the file will be saved.
        format : str, optional
            File format to use: "csv" or "parquet" (default is "csv").

        Raises:
        -------
        ValueError
            If the specified format is not supported.
    '''   
    #Take data recording part of the dataset (no header)
    df = pd.DataFrame(data["rec"])
    #combine date and time into a single index
    
    #rename columns
    df.rename(columns={"kota": "elev"}, inplace=True)
    #Save into the selected format
    if format == "csv":
        file_name = f"station_{station_id}_{date.strftime('%Y%m%d')}.csv"
        save_path = os.path.join(data_dir, file_name)
        df.to_csv(save_path)

    elif format == "parquet":
        file_name = f"station_{station_id}_{date.strftime('%Y%m%d')}.parquet"
        save_path = os.path.join(data_dir, file_name)
        df.to_parquet(save_path)
    else:
        raise ValueError (f'Format {format} cannot be selected, Please choose between "csv" and "parquet".')
    
##################################################################################
#STILL NOT WORKING
#################################################################################


def fetch_hidmet(hm_id, period, url = "https://www.hidmet.gov.rs/latin/osmotreni/nrt_tabela_grafik.php"): 
    '''
        Scrapes water stage measurements from the Hidmet website for a given station and time period.

        Parameters:
        -----------
        hm_id : str or int
            The station ID used by the Hidmet portal.
        period : str
            Time period string as expected by the Hidmet URL (e.g., "1d", "7d", "30d").
        url : str, optional
            Base URL of the Hidmet data endpoint (default is the standard portal URL).

        Returns:
        --------
        pd.DataFrame
            DataFrame with datetime as index and 'stage_cm' as the measurement column.

        Raises:
        -------
        HTTPError
            If the HTTP request fails.
        ValueError
            If no data table is found on the page.
    '''
    params = {"hm_id": hm_id, "period": period}
    complete_url = url + f'?hm_id={hm_id}&period={period}'

    resp = requests.get(complete_url)
    resp.raise_for_status()

    # Parse all tables in the HTML
    tables = pd.read_html(StringIO(resp.text))

    if not tables:
        raise ValueError("No table found on page")

    df = tables[0]  # assuming the first table is what you need
    df.columns = ["datetime", "stage_cm"]
    # Convert types
    df["datetime"] = pd.to_datetime(df["datetime"], format="%d.%m.%Y %H:%M")
    df["stage_cm"] = pd.to_numeric(df["stage_cm"], errors="coerce")
    df.dropna(subset=["datetime"], inplace=True)
    return df.set_index("datetime")

