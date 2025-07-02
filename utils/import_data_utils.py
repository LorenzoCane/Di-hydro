import requests
from bs4 import BeautifulSoup
from io import StringIO
import json
import os
import pandas as pd
import xarray as xr
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
    
def fetch_hidmet(hm_id, period, url = "https://www.hidmet.gov.rs/latin/osmotreni/nrt_tabela_grafik.php"):
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

'''
def fetch_hidmet(hidmed_id, ):

    #Request to the site
    complete_url = url + f'?hm_id={hidmed_id}&period={period}'
    param = {"hm_id": hidmed_id, "period": period}
    r = requests.get(url)
    #check
    r.raise_for_status()

    #Create the soup (Unicode text for the selected HTML site)
    soup = BeautifulSoup(r.text, "html.parser")
    #Search for table in the HTML
    table = soup.find("table")
    #Check
    if table is None:
        raise ValueError (f"No table data found for id : {hidmed_id} , period: {period}")

    #Use the tr HTML command to fetch and parse data
    rows = table.find_all("tr")[1:] #skip header

    
    #HIDMET TABLE structure: 1st coloumn: " Datum i vreme " ("Date and time")
    #                        2nd coloumn: "  Vodostaj (cm) " ("Water level (cm)")
    

    rec = []
    for row in rows:
        #use the HTML column command
        cols = row.find_all("td")
        #Read and save data into an array
        if len(cols) >= 2:
            date_text = cols[0].text.strip()

            if date_text:
                dt = datetime.strptime(date_text, "%d.%m.%Y %H:%M")
            else:
                print(f"[WARNING] Empty date field in row: {cols}")
    
    #        dt = datetime.strptime(cols[0].text.strip(), "%d.%m.%Y %H:%M") #date and time in the format used by HIDMET
            level = float(cols[1].text.strip()) #water level [cm]
            rec.append({"datetime": dt, "water_level_cm": level})

    #save into a DataFrame
    df = pd.DataFrame(rec).set_index("datetime", inplace=True)

    return df
'''

def grib_to_csv(file_path, target_file):
    '''
    
    '''
    #Open dataset
    grib_ds = xr.open_dataset(file_path, engine='cfgrib')
    #To dataFrame
    df = grib_ds.to_dataframe().reset_index()

    #Save to CSV
    df.to_csv(target_file, index=False)
    print(f'File {target_file} converted and save as {target_file}.')