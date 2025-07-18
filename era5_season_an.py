'''

'''

# -------------------------------------------------------------------------------------------
#Import libraries and utils
import os
import json
import numpy as np
import pandas as pd
import xarray as xr 
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import sys

#custom utils
sys.path.insert(0, './utils')
from season_anal_utils import inspect_missing

# -------------------------------------------------------------------------------------------
#Paths and global settings
sep = '-----------------------------------------------------------------------------------------'

era5_variables = ['t2m', 'sde', 'ssro', 'ssrd', 'e', 'tp']
preproc_dir = './preprocessed'
img_dir = './img'
os.makedirs(img_dir, exist_ok=True)

station_id_map = './hydrometrological_data/station_id_name_map.txt'
var_to_units_map = './preprocessed/var_to_units.txt'
# Load the station ID map
with open(station_id_map) as f:
    station_map = json.load(f)

#Load variable  - units map
with open(var_to_units_map) as f:
    var_unit_map = json.load(f)

# -------------------------------------------------------------------------------------------
#Check missing data 
'''
print('Missing data in ERA5 dataset:')
for file in os.listdir(preproc_dir):
    if file.endswith('flattened.parquet'):
        df = pd.read_parquet(os.path.join(preproc_dir, file))
        missing_summary = inspect_missing(df)

print(sep)
print('Missing data in river data:')
for file in os.listdir(preproc_dir):
    if file.endswith('tributaries_merged.parquet'):
        df = pd.read_parquet(os.path.join(preproc_dir, file))
        missing_summary = inspect_missing(df, plot=False)

'''

# -------------------------------------------------------------------------------------------
#Seasonal decomposition 

for variable in era5_variables:
    print(sep)
    print(f'ERA5 - {variable} : Time series decomposition')
    filename = f'era5_{variable}_flattened.parquet'
    units = var_unit_map[variable]['units']
    long_name = var_unit_map[variable]['long_name']
    #find file
    for file in os.listdir(preproc_dir):
        if file == filename :
            print(f'Found dataset...')
            path = os.path.join(preproc_dir, file)

            #Load dataset
            df = pd.read_parquet(path)
            if 'datetime' not in df.columns:
                df.reset_index(inplace=True) #make datetime a column
            df = df.dropna() # (I don't feel of to use fillna )

            #Row-wise avg (--> avg value in the selected area, grid mean)
            df[f'{variable}_mean'] = df.drop(columns='datetime').mean(axis=1)
            mean =   df[f'{variable}_mean']
            #Reset index
            df.set_index('datetime')[f'{variable}_mean'].plot(title=f'ERA5 - {long_name} - Grid mean')
            plt.ylabel(f'{long_name} [{units}]')
            plt.xlabel('Time')
            plt.tight_layout()
            #Save results
            img_name = f'{variable}_mean_over_grid.pdf'
            img_path = os.path.join(img_dir, img_name)
            plt.savefig(img_path)
            print(f'Mean over time plot save to {img_path}')
            #Clear plot
            plt.clf()

            seas_decomp = seasonal_decompose(mean, period=365)
            seas_decomp.plot()
            img_name = f'{variable}_seasonal_decomp.pdf'
            img_path = os.path.join(img_dir, img_name)
            plt.savefig(img_path)
            print(f'Seasonal decomposition plot save to {img_path}')
            #Clear plot
            plt.clf()

            plot_acf(mean)
            plt.show()




