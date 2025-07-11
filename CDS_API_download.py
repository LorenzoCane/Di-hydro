'''
    CDS API request and download

    This script downloads the requested quantities for specific frequency and time range.
    The data are downloaded as monthly-aggregated ".nc" file (the original downloaded files are zipped
    but the script extract them in the corresponding year folder)
    For further info refer to : https://cds.climate.copernicus.eu/how-to-api)

    It depends on common libraries, please install al the deèendancies listed in "requirements.txt"

    Functions:
    - extract_nc : Extract the .nc files from the zip file, rename it and save it into a user-selected folder

    Author: Lorenzo Cane - DBL E&E Area Consultant
    Last Modified: 08/07/2025
'''

#Imports 
import os
from zipfile import ZipFile
import xarray as xr
import pandas as pd
import cdsapi
import cfgrib

# -------------------------------------------------------------------------------------------
#Definition of path and variables

#Dir where to put nc files
download_dir = './ERA5_data/'
os.makedirs(download_dir, exist_ok=True)

dataset = 'reanalysis-era5-land'
#Downloaded variables
variables = [
            '2m_temperature', 'snow_depth', 'surface_runoff' 'surface_pressure', 'sub_surface_runoff','surface_solar_radiation_downwards',
			'total_evaporation', 'total_precipitation'
            ]
#time range definition
years = list(range(2020, 2025))
months = list(range(1, 13)) # (1,13) for full year (REMEMBER: last month is not included)
days = [f"{d:02d}" for d in range(1, 32)] # !!! last number is not included: (1,32) for full month
time = [f"{h:02d}:00" for h in range(24)] #Already in the ERA5 correct format

#Area of Interest
area = [44.5, 19.5, 43.5, 20.83]  # North, West, South, East

# -------------------------------------------------------------------------------------------
#Function definition
def extract_nc(zip_path, extracted_dir, target_name):
    '''
        Extract a file from a ZIP archive and rename it during extraction.

        Parameters:
        ----------
        zip_path : str
                Path to the ZIP archive containing the file to be extracted.
        
        extracted_dir : str
                Directory where the extracted file should be placed.
        
        target_name : str 
                New name to assign to the extracted file (useful for renaming generic or repeated filenames 
                like 'data.nc' to something unique or descriptive).

        
        Return:
        ----------
        None

        Notes:
        ----------
        - This does not alter the content of the ZIP archive.
    '''
    with ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.infolist():
            filename = file.filename #needed by .extract
            file.filename = target_name # Change the filename in memory (temporary change, does not alter the zip file itself)
            zip_ref.extract(filename, path=extracted_dir)
    print(f'Extracted: {zip_path} into {extracted_dir}')
    
# -------------------------------------------------------------------------------------------
# Download loop

for year in years:
    #year sub-folder into ERA5 data folder
    year_dir = os.path.join(download_dir, str(year))
    os.makedirs(year_dir, exist_ok=True)
    
    for month in months:
        month_str = f"{month:02d}"
        print("\n************************************************")
        print(f"Year: {year}, Month: {month_str}")
        print("************************************************")
        #main part of name
        name_file_base = f'ERA5_{year}_{month_str}'
        name_file_base_path = os.path.join(year_dir, f'ERA5_{year}_{month_str}')
        target_zip= f"{name_file_base}.zip"
        target_nc = name_file_base + '.nc'
        
        # ERA5-land request
        request = {
            'product_type': 'reanalysis',
            'variable': variables,
            'year': year,
            'month': month,
            'day': days,
            'time': time,
            'area': area,
            'format': 'netcdf'
        }
        
        # Download
        if not os.path.exists(target_zip): #do avoid useles download
            print(f'Downloading {name_file_base}...')
            # Set CDS API client
            client = cdsapi.Client()
            client.retrieve(dataset, request, target_zip)
        else:
            print(f'Zip already exists: {target_zip}')
                
        #Extract and rename
        extract_nc(target_zip, year_dir,target_nc)
        