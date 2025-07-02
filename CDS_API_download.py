'''
    CDS API request and download

    This script downloads the requested quantities for specific frequency and time range.
    (Original script : https://cds.climate.copernicus.eu/how-to-api)
'''
import os
import zipfile
import xarray as xr
import pandas as pd
import cdsapi
import cfgrib
from eccodes import codes_index_new_from_file, codes_index_get, codes_index_select


def list_shortnames(grib_file):
    try:
        index = cfgrib.open_fileindex(grib_file, filter_by_keys={'edition': 2})
        shortnames = set(index['shortName'].values)
        index.close()
        return shortnames
    except Exception as e:
        print(f"cfgrib indexing error: {e}")
        return []

def extract_and_grib_to_csv(zip_path, extracted_dir, output_csv_base):
    '''
    Extracts GRIB files from ZIP and saves each variable (shortName) as a separate CSV.
    '''
    os.makedirs(extracted_dir, exist_ok=True)
    
    # Step 1: Unzip
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_dir)
    print(f'Extracted: {zip_path} into {extracted_dir}')
    
    # Step 2: Find GRIB file
    grib_file = None
    for root, _, files in os.walk(extracted_dir):
        for file in files:
            if file.endswith('.grib') or file.endswith('.grb'):
                grib_file = os.path.join(root, file)


                # List variables
                shortnames = list_shortnames(grib_file)
                print(f"Variables found: {shortnames}")

                for var in shortnames:
                    try:
                        ds = xr.open_dataset(grib_file, engine='cfgrib', backend_kwargs={
                            'filter_by_keys': {'shortName': var, 'edition': 2}
                        })
                        df = ds.to_dataframe().reset_index()
                        out_csv = f"{output_csv_base}_{var}.csv"
                        df.to_csv(out_csv, index=False)
                        print(f"Saved {var} to {out_csv}")
                    except Exception as e:
                        print(f"Failed to extract {var}: {e}")

# -------------------------------------------------------------------------------------------
# Download loop

download_dir = './GRIB_download/'



dataset = 'reanalysis-era5-land'
variables = [
  '2m_dewpoint_temperature', '2m_temperature', 'leaf_area_index_high_vegetation', 'snow_depth', 'snow_density'
					'surface_runoff' 'surface_pressure', 'sub_surface_runoff','surface_solar_radiation_downwards',
					'total_evaporation', 'total_precipitation'
]

years = list(range(2020, 2025))
months = list(range(1, 13))
days = [f"{d:02d}" for d in range(1, 32)]
time = [f"{h:02d}:00" for h in range(24)]
area = [44.5, 19.5, 43.5, 20.83]  # North, West, South, East

for year in years:
    year_dir = os.path.join(download_dir, str(year))
    os.makedirs(year_dir, exist_ok=True)
    
    for month in months:
        month_str = f"{month:02d}"
        print("\n************************************************")
        print(f"Year: {year}, Month: {month_str}")
        print("************************************************")
        
        extracted_dir = os.path.join(year_dir, 'extracted_zip')
        os.makedirs(extracted_dir, exist_ok=True)
        
        name_file_base = os.path.join(year_dir, f'ERA5L_{year}_{month_str}')
        target_zip = f"{name_file_base}.nc"
        
        # ERA5-land request
        request = {
            'product_type': 'reanalysis',
            'variable': variables,
            'year': year,
            'month': month,
            'day': days,
            'time': time,
            'area': area,
            'format': 'netcdf',
        }
        
        # Download
        if not os.path.exists(target_zip):
            print(f'Downloading {target_zip}...')
            # Set CDS API client
            client = cdsapi.Client()
            client.retrieve(dataset, request, target_zip)
        else:
            print(f'Zip already exists: {target_zip}')
        
        #Extract and convert
        extract_and_grib_to_csv(target_zip, extracted_dir, name_file_base)