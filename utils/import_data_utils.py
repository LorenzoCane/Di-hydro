import requests
import json
import os
import pandas as pd
from datetime import datetime, timedelta

def get_station_id_basin_map(url, placeholder_id = 237, option = 1):
    '''
     Fetch data from the given url API, returns a mapping of station IDs to station basin and station name.

     Parameters:
     -----------
     url : str | .php url of one of the station used to fetch ids and name from
     placeholder_ id : int, optional | ID of one of the station. This is the station to query.
     option : int, optional | Option parameter for API. Default = 1

     Returns:
     -----------

     dict: Map if station ID (str) to a dict with 'name' and 'basin'.
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