'''
    Preprocessing of ERA5-land and river level data

    This script is part of the Di-hydro data preparation pipeline.
    It processes satellite-based ERA5-land reanalysis data and observed hydrometeorological
    river level data, preparing them for machine learning model training.

    Main features:
    - Flatten ERA5 NetCDF variables and save them to columnar format (optional).
    - Create PyTorch-like tensors of ERA5 variables for time-series modeling (optional).
    - Filter and merge river level measurements into one aligned DataFrame (optional).

    Note:
    - Sections are optional and can be skipped 
      once preprocessed files are available.
    - Outputs are stored in the './preprocessed' folder.

    Author: Lorenzo Cane - DBL E&E Area Consultant
    Last Modified: 17/07/2025
'''

# -------------------------------------------------------------------------------------------
#Import libraries and utils
import os
import numpy as np
import pandas as pd
import xarray as xr
import json
from functools import reduce
from tqdm import tqdm
import sys
#custom utils
sys.path.insert(0, './utils')
from preproc_utils import load_hydro_data, flat_ERA5_data, get_flat_index_to_coords, tensor_ERA5_pytorch, filter_river_data, rename_column


# -------------------------------------------------------------------------------------------
#Paths and global settings
sep = '-----------------------------------------------------------------------------------------'

era5_variables = ['t2m', 'sde', 'ssro', 'ssrd', 'e', 'tp']
hydrometr_dir = './hydrometrological_data' #hydrometrological data main folder
hydro_subdir_names = []
era5_dir = './ERA5_data' #ERA5 data main folder


preproc_dir = './preprocessed'
os.makedirs(preproc_dir, exist_ok=True)

expected_dim = 11 * 14

# Load the station ID map
with open("./hydrometrological_data/station_id_name_map.txt") as f:
    station_map = json.load(f)

#********************************************************************************************
# 1) ERA5 flattened version + coordinate mapping

#Loop through all variables
for var in tqdm(era5_variables):
    print(sep)
    print(f'Working on variable {var}....')

    #empty array to store partial records
    all_records = []
    #output file name
    output_name = f'era5_{var}_flattened.parquet'
    output_file = os.path.join(preproc_dir, output_name)

    #Loop through all NetCDF files
    for root, dirs, files in os.walk(era5_dir):
        for file in files:
            if file.endswith('.nc'):
                file_path = os.path.join(root, file)
                print(f'Processing file: {file_path}')

                record = flat_ERA5_data(file_path, var)
                all_records.extend(record)


    #to Dataframe and save
    df = pd.DataFrame(all_records)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime").reset_index(drop=True)
    print(f'Check Dataframe variable {var}:')
    print(df.head(10))

    df.to_parquet(output_file, index=False)

    print(f'Flattened data file of {var} saved to {output_file}')

#Create index - coordinate map
example_ds = './ERA5_data/2019/ERA5_2019_01.nc'
ds = xr.open_dataset(example_ds)

index_to_coord = get_flat_index_to_coords(ds)

map_filename = 'index_to_coord.txt'
map_path = os.path.join(preproc_dir, map_filename)

with open(map_path, 'w') as f:
    f.write(json.dumps(index_to_coord))
#********************************************************************************************
# 2) ERA5 grid version 

#Loop through all variables
for var in tqdm(era5_variables):
    print(sep)
    print(f'Working on variable {var}....')

    output_name = f'era5_{var}_tensor.npz'
    output_path =  os.path.join(preproc_dir, output_name)

    var_tens, var_timestamp = tensor_ERA5_pytorch(era5_dir, var)

    #Save results in NumpyZip format
    np.savez_compressed(output_path, tensor=var_tens, timestamps=np.array(var_timestamp, dtype='datetime64[ns]'))

    print(f'Tensor for variable {var} saved to {output_path}')

'''
**************************************************************************
**************************************************************************
IMPORTANT NOTES
**************************************************************************
**************************************************************************
Always use timestamp and tensor together: data in tensor are not time ordered.
Timestamp as been saved as datatime64. While loading use:
    data = np.load("*.npz", allow_pickle=True)
    tensor = data["tensor"]                   # shape: (N, 1, H, W)
    timestamps = data["timestamps"].tolist()  # list of datetime64
    timestamps = pd.to_datetime(timestamps)
'''

#********************************************************************************************
# 3) Filter and merge River level data

river_codes = ['236', '237', '238', '239', '240']
excluded_stations = {"240"}  # station IDs to exclude from merged file
all_river_dfs = []

merged_file_name = 'tributaries_merged.parquet'
merged_file_path = os.path.join(preproc_dir, merged_file_name)

#Loop through rivers
for code in river_codes:
    print(sep)
    print(f'Processing river {code}')

    single_file_name = f'river_{code}_level_merged.parquet'
    output_path = os.path.join(preproc_dir, single_file_name)
    river_df = filter_river_data(hydrometr_dir, code)

    if river_df is not None:
        #Sort and save
        river_df= river_df.sort_values('datetime').reset_index(drop=True)
        river_df.to_parquet(output_path, index = False)
        #Visual check
        print(river_df.head(10))
        if code not in excluded_stations:
            all_river_dfs.append(river_df)
    else:
        raise ValueError(f'Empty DataFrame while processing river {code}')


#Merge on datetime and sort
print(sep)
print('Merging tributaries data...')

merged_df = reduce(lambda left, right: pd.merge(left, right, on="datetime", how="outer"), all_river_dfs)
merged_df = merged_df.sort_values("datetime").reset_index(drop=True)

print(merged_df.head(10))

#Save
merged_df.to_parquet(merged_file_path, index=False)
print(f'Merged data saved to {merged_file_path}')