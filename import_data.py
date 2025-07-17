"""
    Hydrometrological Station Data Downloader

    This script downloads daily hydrometrological data from the MeteoSRS online service for selected
    stations over a defined time range. The data is retrieved via HTTP POST requests, and parsed JSON
    responses are stored in a structured folder hierarchy based on station and year.

    Workflow:
    ---------
    - Retrieve mapping between station IDs and their associated names/basins.
    - For each station and each day within the defined date range:
        - Query the online data endpoint.
        - If data is present, save it in a JSON file named by date.
    - Store all files in an output directory, grouped by basin/station and year.

    Inputs:
    -------
    - Station IDs
    - Date range (start and end)
    - API endpoints for station metadata and daily data

    Outputs:
    --------
    - `station_id_name_map.txt`: JSON dictionary of ID-to-name/basin mapping.
    - Daily `.json` files per station, organized by year.

    Dependencies:
    -------------
    - Python libraries
    - import_data_utils (fetch_hydrometr_data, save_daily_data, get_station_id_basin_map) - custom module


    ATTENTION:
    Data units are defined as follows:
    - temp     [°C]
    - level    [cm]
    - elev     [cm msl]  (centimeters above mean sea level)
    - battery  [V]

    Author: Lorenzo Cane - DBL E&E Area Consultant  
    Last modified: 20/06/2025
"""
import requests
from tqdm import tqdm
import json
from datetime import datetime, timedelta
import os
import sys
#custom utils
sys.path.insert(0, './utils')
from import_data_utils import fetch_hydrometr_data, save_daily_data, get_station_id_basin_map

#----------------------------------------------------------------------------------------------
sep = '=================================================='

#Output dirictory and filename
output_dir = "./hydrometrological_data"
os.makedirs(output_dir, exist_ok=True)
id_name_file = 'station_id_name_map.txt' #ID-name map file
id_file_path = os.path.join(output_dir, id_name_file)

#Station config and API endpoints
station_ids = [239]   # [236, 237, 238, 239, 240]  # Add other known station IDs
station_map_url = "http://www.meteos.rs/ahs/elektromorava/getmaindata.php"
data_url = "http://www.meteos.rs/ahs/elektromorava/getdata.php"

#Start and end date in yyyy,m,d(d) format
start_date = datetime(2019, 6, 10) # start at 2019, 6, 10
end_date = datetime(2020,1,1)

delta_t = timedelta(days=1)


#----------------------------------------------------------------------
#Create a map between station IDs, names and basins
map_dict = get_station_id_basin_map(station_map_url)
#print(map_dict)
with open(id_file_path, 'w', encoding="utf-8") as file:
    json.dump(map_dict, file, indent=2, ensure_ascii=False)
print(f'Station IDs map created and saved in {id_file_path}')
print(sep)

# ----------------------------------------------------------------------
# Main loop - Save hydrometrological data for the selected stations 
for station in station_ids:
    info_station = map_dict.get(str(station), {})
    st_basin = info_station.get("basin", "Unknown")
    print(f'Fetching station {st_basin} - {station} data...')
    
    total_days = (end_date - start_date).days + 1
    # Reset current date to start date
    cur_date = start_date

    with tqdm(total=total_days, desc=f"Station {station} ({st_basin})") as pbar:

        while cur_date <= end_date:
            try:
                json_data = fetch_hydrometr_data(data_url, station, cur_date)
                # No data exception
                if "rec" in json_data and json_data["rec"]:
                    # Directory structure: ./output_dir/{station name - ID}/{year}/
                    year_str = str(cur_date.year)
                    station_dir = f"{st_basin} - {station}"
                    station_path = os.path.join(output_dir, station_dir, year_str)
                    os.makedirs(station_path, exist_ok=True)
                
                    save_daily_data(json_data, station, cur_date, station_path)
                else:
                    print(f'No data for station {st_basin} - {station} on {cur_date.date()}')

            except Exception as e:
                    print(f'Error in station {st_basin} - {station} on {cur_date.date()} : {e}')
        
            cur_date += delta_t
            pbar.update(1)
        print(f'--------------------------')
