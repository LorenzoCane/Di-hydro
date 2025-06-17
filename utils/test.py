
from import_data_utils import fetch_hidmet

df =  fetch_hidmet(hm_id= 47101, period=7)

print(df)
#df.to_parquet("test_output/test_hidmet_fetch.parquet")