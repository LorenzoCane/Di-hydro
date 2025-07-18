'''
    Preprocessing utils

    This module provides functions to retrieve, process, and transform ERA5 climate reanalysis data 
    and river hydrometric observations for integration into hydrological modeling and machine learning pipelines. 
     It includes utilities for extracting flattened ERA5 grids, converting them into PyTorch-ready tensors, 
    filtering river level data, and generating spatial index mappings.

    Functions:
    ----------
    - load_hydro_data:
        Loads and concatenates hydrometric data for a specific date string from raw CSV files.

    - flat_ERA5_data:
        Flattens ERA5 variable values (e.g., temperature, pressure) into tabular format for ML integration.

    - get_flat_index_to_coords:
        Returns a dictionary mapping flattened ERA5 grid indices to geographic coordinates (lat, lon).

    - tensor_ERA5_pytorch:
        Converts gridded ERA5 NetCDF files into PyTorch-ready tensors of shape (N, 1, H, W), 
        where N is the number of time steps.

    - filter_river_data:
        Extracts and cleans hydrometric water level time series for a given station ID from raw CSV files.

    - rename_column:
        Renames a river column based on its metadata using a provided station map 
        (e.g., from ID to human-readable basin name).

    Dependancies:
    ------------
    - Python libraries (see requuirements.txt file)

    Notes:
    ------
    - ERA5 data should be organized in yearly folders with monthly `.nc` files.
    - This module assumes a 11x14 grid resolution for spatial data by default.
'''

import os
import numpy as np
import pandas as pd
import xarray as xr
import json
from datetime import datetime
import matplotlib.pyplot as plt
from tqdm import tqdm

def load_hydro_data(date_str, hydrometr_dir='./hydrometrological_data'):
    '''
        Load hydrometric CSV data for a specific date string from a directory structure.

        Parameters:
        ----------
            date_str: str
                 Date in 'YYYY-MM-DD' or other substring format to match in filenames.
            hydrometr_dir: str , OPT
                Root directory containing CSV files of hydrometric measurements.

        Returns:
        --------
        pd.DataFrame or None:
            Concatenated dataframe of matched records with a timestamp column,
            or None if no files match.
    '''
    matched_data = [] #array to store matched data based on date
    
    for root, dirs, files in os.walk(hydrometr_dir): #check all subdirs
        for file in files:                           #check all files
            if date_str in file and file.endswith('.csv'): #check file name and format
                file_path = os.path.join(root, file)

                try:
                    df = pd.read_csv(file_path)
                    df['timestamp'] = pd.to_datetime(df['sdate'] + " " + df['stime'])
                    matched_data.append(df)

                except Exception as e:
                    print(f'Failed to read {file_path}: {e}')

    return pd.concat(matched_data, ignore_index=True) if matched_data else None

def flat_ERA5_data(file_path, variable_name, dimension=11*14):
    '''
        Flatten ERA5 variable data from NetCDF into 1D arrays with time-based indexing.

        Parameters:
        -----------
        file_path : str
            Path to the NetCDF file (.nc).
        variable_name: str
            Name of the ERA5 variable to extract.
        dimension : int , opt 
            Expected spatial resolution (default 154 = 11x14 for lat x lon).

        Returns:
        --------
        list[dict]: 
            A list of dictionaries where each contains flattened variable values and a timestamp.
    '''
    #Array to save partial records
    file_record = []
    #Open file
    try:
        ds = xr.open_dataset(file_path)
    except Exception as e:
        print(f'Failed to open {file_path}: {e}')
    
    #Look for variable 
    if variable_name not in ds:
        raise ValueError(f"Variable '{variable_name}' not found in dataset.")
    
    var_data = ds[variable_name] #shape: (time, lat , long)

    #Flat data iterating over time
    time_values = ds["valid_time"].values
    for i,t in enumerate(time_values): 
        flat = var_data.isel(valid_time=i).values.flatten() #FLATTEN move on lat then long (north 2 south , then west 2 east)
        record = {"datetime" : pd.to_datetime(t)}
        record.update({f"{variable_name}_{j}": flat[j] for j in range(len(flat))})
        file_record.append(record)

    if (len(flat) != dimension):
        print(f'ALERT: record dimension is {len(flat)} while expected dimension is {dimension}')

    return file_record
              

def get_flat_index_to_coords(ds):
    """
        Returns a dictionary mapping each flattened index of a variable to its (lat, lon) coordinate.
    
        Parameters:
        -----------
        ds: xarray.Dataset
            The dataset containing the variable.
        
        Returns:
        --------
        dict: 
            Mapping from index (int) to (lat, lon) tuple.
    """

    lats = ds.latitude.values
    lons = ds.longitude.values
    
    mapping = {}
    idx = 0
    for lat in lats:
        for lon in lons:
            mapping[idx] = (lat, lon)
            idx += 1
    return mapping


def tensor_ERA5_pytorch(main_dir, variable):
    """
        Converts ERA5 variable data from multiple NetCDF files into PyTorch-compatible tensor format.
        (Automatic scan of subdirs is implemented).
        
        Parameters:
        -----------
        main_dir: str
            Root directory containing NetCDF files.
        variable: str
            Name of the ERA5 variable to extract.

        Returns:
        --------
        tuple:
            - numpy.ndarray: 
                Tensor of shape (N, 1, H, W) where N is the number of time steps.
            - list[pandas.Timestamp]: 
                Corresponding datetime objects for each time step.
    """

    #empty array where to store  the results
    tensors = []
    timestamps = []

    #Loop through all files
    for root, dirs, files in os.walk(main_dir):
        for file in files:
            if file.endswith('.nc'):
                file_path = os.path.join(root, file)
                print(f'Processing file: {file_path}')
                #Read dataset
                ds = xr.open_dataset(file_path)
                #Check for variable
                if variable not in ds:
                    continue
                
                #Time and variable values
                time_vals = ds['valid_time'].values
                var_vals = ds[variable].values #Still in shape : (time, lat, long)
                
                #Loop on time dime
                for i in range(var_vals.shape[0]):
                    #Create time slices
                    grid = var_vals[i, : , : ] #shape : (lat, long)
                    #tensor like grid
                    grid_tensor = grid[np.newaxis, : , : ]  #shape : (1, lat, long)

                    #Store grid in tensor and corresponding timestamp
                    tensors.append(grid_tensor)
                    timestamps.append(pd.to_datetime(time_vals[i]))       

    #Create a PyTorch-friendly tensor (stack sequence of arrays along a new axis)
    tensor = np.stack(tensors) #shape: (N, 1, H, W)

    return tensor.astype(np.float32), timestamps


def filter_river_data(main_dir, river_code, battery_treshold = 12.0):
    '''
        Load, filter, and clean river-level hydrometric data for a given river code.
        Filtering process is based on battery voltage and physical meaning of level.
        Automatic subdirs scan on.

        Parameters:
        -----------
        main_dir: str
            Directory containing the CSV files for different stations.
        river_code: str 
            Unique identifier for the river station.
        battery_treshold: float, opt
            Minimum battery level threshold for valid data (default = 12.0).

        Returns:
        --------
        pandas.DataFrame or None: 
            Filtered time series dataframe with datetime and level columns, or None if no data found.
    '''
    river_name = f'river{river_code}_level' #idx name
    dfs = [] #final dataframe

    #Loop throught all subdirs (ready for all subdirs structure)
    for root, dirs, files in os.walk(main_dir):
        for file in files:
            #Find the right files
            if file.endswith('.csv') and f'station_{river_code}_' in file:
                file_path = os.path.join(root, file)
                #Read csv
                df = pd.read_csv(file_path)
                df['datetime'] = pd.to_datetime(df['sdate'] + ' ' + df['stime'])
                #Clean Dataset using battery level thr. and imposing level > 0
                df = df[(df['battery'] >= battery_treshold) & (df['level'] >= 0)]
                #Rename coloumn
                df = df[['datetime', 'level']].rename(columns={'level': river_name})
                #Store all data from the same river
                dfs.append(df)

    if dfs:
        return pd.concat(dfs).drop_duplicates('datetime')
    else:
        print('DataFrame is empty.')
        return None
    
def rename_column(col, station_map):
    '''
        Rename river column based on a station metadata map (e.g., from ID to basin name).
        Ideal for human-readablility

        Parameters:
        -----------
        col: str 
            Original column name (e.g., 'river001_level').
        station_map : dict 
            Dictionary mapping station ID to metadata including 'basin' name.

        Returns:
        --------
        str: 
            Cleaned and renamed column name for clarity.
    '''
    
    if col.startswith("river") and col.endswith("_level"):
        station_id = col.replace("river", "").replace("_level", "")
        if station_id in station_map:
            name = station_map[station_id]["basin"]
            return name.replace(" ", "_")  # make it column-friendly
    return col  # fallback for datetime or unmatched


def get_unit_longname(ds, variable):
    '''
    '''

    #Variable subset
    subset = ds[variable].isel(valid_time = 0)
    if subset is None:
        raise ValueError(f'variable Subset is empty, not able to detect unit and long name')
    unit = subset.attrs['units']
    long_name =  subset.attrs['long_name']

    return unit, long_name