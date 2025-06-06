import requests
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

station_ids = [236, 237, 238, 239, 240]  # Add other known station IDs
station_map_url = "http://www.meteos.rs/ahs/elektromorava/getmaindata.php"
data_url = "http://www.meteos.rs/ahs/elektromorava/getdata.php"

#Start and end date in yyyy,m,d format
start_date = datetime(2025, 5, 1)
end_date = datetime(2025, 5, 31)

delta_t = timedelta(days=1)


#----------------------------------------------------------------------
#Create a map between station IDs, names and basins
map_dict = get_station_id_basin_map(station_map_url)
#print(map_dict)
with open(id_file_path, 'w', encoding="utf-8") as file:
    json.dump(map_dict, file, indent=2, ensure_ascii=False)
print(f'Station IDs map created and saved in {id_file_path}')
print(sep)

#----------------------------------------------------------------------
#Save hydrometrologival data for the selected stations

for station in station_ids:
    info_station = map_dict.get(str(station), {})
    st_basin = info_station.get("basin", "Unknown")
    print(f'Fetching station {st_basin} - {station} data...')
    #create sub dict
    station_dir = f"{st_basin} - {station}"
    station_path = os.path.join(output_dir, station_dir)
    os.makedirs(station_path, exist_ok=True)
    #reset current date to start date
    cur_date = start_date
    while cur_date <= end_date:
        try:
            json_data = fetch_hydrometr_data(data_url, station, cur_date)
            #No data exception
            if "rec" in json_data and json_data["rec"]:
                save_daily_data(json_data, station, cur_date, station_path)
            else:
                print(f'No data for station {st_basin} - {station} on {cur_date.date()}')

        except Exception as e:
            print(f'Error in station {st_basin} - {station} on {cur_date.date()} : {e}')
        
        cur_date += delta_t
        print(f'--------------------------')


'''
ATTENTION:
    DATA UNITS ARE A BIT STRANGE:
    - temp [˚C]
    - level [cm]
    - elev [10^-5 m]
    - battery [V]

'''

