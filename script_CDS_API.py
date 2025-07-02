#!/usr/bin/env python
import cdsapi

years = list(range(2023, 2024))
months = list(range(2, 13))

for cds_year in years:
	for cds_month in months:
	
		print("************************************************")
		print("year: ", cds_year, ", month: ", cds_month)
		print("************************************************")
		
		name_month = str(cds_month)
		if cds_month < 10: name_month = '0' + str(cds_month)
		
		name_dir = 	str(cds_year) + '/'
		name_file = name_dir + 'ERA5L_'+ str(cds_year) + '_'+ name_month + '_varselec1.netcdf.zip'
		
		c = cdsapi.Client()
		c.retrieve(
	    	'reanalysis-era5-land',
	    	{
	    	    'variable': [
	    	        '2m_dewpoint_temperature', '2m_temperature', 'leaf_area_index_high_vegetation', 'snow_depth', '	snow_density'
					'surface_runoff' 'surface_pressure', 'sub_surface_runoff','surface_solar_radiation_downwards',
					'total_evaporation', 'total_precipitation'
	    	    ],
	    	    'year': cds_year,
	    	    'month': cds_month,
	    	    'day': [
	    	        '01', '02', '03',
	    	        '04', '05', '06',
	    	        '07', '08', '09',
	    	        '10', '11', '12',
	    	        '13', '14', '15',
	    	        '16', '17', '18',
	    	        '19', '20', '21',
	    	        '22', '23', '24',
	    	        '25', '26', '27',
	    	        '28', '29', '30',
	    	        '31',
	    	    ],
	    	    'time': [
	    	        '00:00', '01:00', '02:00',
	    	        '03:00', '04:00', '05:00',
	    	        '06:00', '07:00', '08:00',
	    	        '09:00', '10:00', '11:00',
	    	        '12:00', '13:00', '14:00',
	    	        '15:00', '16:00', '17:00',
	    	        '18:00', '19:00', '20:00',
	    	        '21:00', '22:00', '23:00',
	    	    ],
	    	    'area': [
	    	        44.5, 19.5,43.5,
	    	        20.83,
	    	    ],
	    	    'format': 'netcdf.zip',
	    	},
	    	name_file)

