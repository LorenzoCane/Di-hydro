# Di-hydro - Data processing pipeline

## Overview 

This repo is a collection of scripts that I have developed and used in the preliminary phase (data searching and acquisition) of a broader project building a **machine learning (ML) model to predict river water levels** using satellite data. The focus is on **supporting Hydropower Plant (HPP)** operations and maintenance through improved forecasting.

This repository provides utilities to:
 - **Download reanalysed climate data** from the [ERA5-land hourly dataset](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land?tab=overview) (via Copernicus CDS API)
 - **Collect in-situ hydrometeorological data** from the [METEOS Elektromorava dataset](http://www.meteos.rs/ahs/elektromorava/)
 - **Extract tabular data from images**, using OCR (Work in progress)
 - Organize dataset for ML-ready processing

## Repository Structure
```
├── ERA5_data/                      # ERA5 reanalysis data organized by year
│       ├── 2019/
│       ├── 2020/
│       └── ...
├── flow_data/
│       └── flow_may_2025.csv      # Example flow data for May 2025
├── hydrometrological_data/        # In-situ station data from Meteos.rs
│       ├── Bjelica - 239/
│       ├── Djetinja - 237/
│       ├── Moravica - 238/
│       ├── Skrapež - 236/
│       ├── Zapadna Morava Radar - 240/
│       └── station_id_name_map.txt # Station ID-to-name reference
├── utils/                         # Helper functions and utilities
│       ├── img_to_csv_utils.py    # OCR and image-table extraction utilities
│       ├── import_data_utils.py   # Meteos.rs data downloader functions
│       └── test.py                # Test scrpit
├── CDS_API_download.py          # ERA5 download script using CDS API
├── script_CDS_API.py            # Alternative version of the above
├── import_data.py               # Download from meteos.rs API
├── img_to_csv_data.py           # Extract table data from scanned images via OCR
├── requirements.txt             # Required Python packages
├── .gitignore                   # Git ignore rules
└── README.md                    # Project documentation
```


## Getting Started & Usage

### 1. Install Dependencies
Ensure you have **Python 3.8 or higher** installed and the repository proper downloaded. Then in the repository in can run:
```
pip install -r requirements.txt
```

### 2. Configure ERA5 Data Access
To use the [CDS API downloader](CDS_API_download.py), you need to configure the Copernicus CDS API (if not already done):
 - Register your self  in the [Copernicus page](https://accounts.ecmwf.int/auth/realms/ecmwf/protocol/openid-connect/auth?client_id=cds&scope=openid%20email&response_type=code&redirect_uri=https%3A%2F%2Fcds.climate.copernicus.eu%2Fapi%2Fauth%2Fcallback%2Fkeycloak&state=1Dmc7R8xfXzErvruclyu5G3abQLAbDVba-1qV8jtCyM&code_challenge=Fsa09MEpA-Rgtrc1MlTnYflPtGUEqATVMDss8iQMkuA&code_challenge_method=S256) and then login
 
 - Setup your **CDS API personal access token** following the [Copernicus page instructions](https://cds.climate.copernicus.eu/how-to-api).

### 3.Download ERA5-land Data
Now you can run: 
```
python CDS_API_download.py
```
this line will automatically create all the directories and subdirectories. Please, open the python script and get familiar with the naming convention. Feel free to adapt it to your personal taste!

```
TIPS: Downloading ERA5 data can take a long time. 
Running the script during free time or night time is strongly suggeested.
```
### 4. Download In-situ Data from Meteos.rs
Run the script to fetch and save time series from Elektromorava stations:
```
python utils/import_data_utils.py
```
Data is saved under ```hydrometrological_data/```.


## Coming Next

- OCR implementation

- ML models for river level prediction (Random Forests, XGBoost, LSTM).


## Git Recomandation 
Use the following in .gitignore to avoid versioning unnecessary data:
```
# Data and output files
*.csv
*.zip
*.nc

# Large folders
ERA5_data/
img_tb_converted/

# Python cache
__pycache__/
```