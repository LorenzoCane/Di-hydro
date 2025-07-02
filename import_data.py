import requests
from tqdm import tqdm
import json
from datetime import datetime, timedelta
import os
import sys
sys.path.insert(0, './utils')
from import_data_utils import fetch_hydrometr_data, save_daily_data, get_station_id_basin_map

sep = '=================================================='
#Output dir
output_dir = "./hydrometrological_data"
os.makedirs(output_dir, exist_ok=True)
id_name_file = 'station_id_name_map.txt'
id_file_path = os.path.join(output_dir, id_name_file)

station_ids = [237, 238]   # [236, 237, 238, 239, 240]  # Add other known station IDs
station_map_url = "http://www.meteos.rs/ahs/elektromorava/getmaindata.php"
data_url = "http://www.meteos.rs/ahs/elektromorava/getdata.php"

#Start and end date in yyyy,m,d format
start_date = datetime(2023, 8, 22) # start at 2019, 6, 10
end_date = datetime(2025, 6, 10)

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
# Save hydrometrological data for the selected stations
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
                    # Create year-based subdirectory
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
'''
ATTENTION:
    DATA UNITS ARE A BIT STRANGE:
    - temp [˚C]
    - level [cm]
    - elev [10^-5 m]
    - battery [V]

'''

