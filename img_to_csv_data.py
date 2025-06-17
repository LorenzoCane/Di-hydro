
import os
import sys
import pandas as pd 
sys.path.insert(0, './utils')
from img_to_csv_utils import enhance_image_for_ocr, extract_protok_data

input_img_dir = './img_tb_converted'
flow_dir = './img_tb_converted/Protoci_maj_2025'
level_dir = './img_tb_converted/Nivoi_maj_2025'

extracted_flow_data_dir = './flow_data'
extracted_level_data_dir = './level_data'
flow_file = "flow_may_2025.csv"
level_file = "level_may_2025.csv"

flow_path = os.path.join(extracted_flow_data_dir, flow_file)
level_path = os.path.join(extracted_level_data_dir, level_file)

os.makedirs(extracted_flow_data_dir, exist_ok=True)
os.makedirs(extracted_level_data_dir, exist_ok=True)

#Extract flow data
all_data = []
for fname in sorted(os.listdir(flow_dir)):
    if fname.endswith(".jpg"):
        image_path = os.path.join(flow_dir, fname)
        all_data.extend(extract_protok_data(image_path))

df = pd.DataFrame(all_data, columns=["Date", "Value1", "Value2", "Value3"])
df.to_csv(flow_path, index=False)

print(f"Flow data saved in {flow_path}")

