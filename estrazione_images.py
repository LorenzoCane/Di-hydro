import zipfile
import os
import re
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pandas as pd

# --- CONFIGURAZIONE ---
zip_dir = './zipfile/'
zip_names = ["Nivoi_maj_2025.zip"]
zip_path = "Protoci_maj_2025.zip"  # il tuo file ZIP
extract_dir = "protoci_extracted"
output_csv = "protoci_maj_2025.csv"

# --- ESTRAZIONE ZIP ---
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

# --- FUNZIONE DI MIGLIORAMENTO IMMAGINE ---


# --- ESTRAZIONE DATI DA UN'IMMAGINE ---


# --- ESECUZIONE OCR SU TUTTE LE IMMAGINI ---
all_data = []
for fname in sorted(os.listdir(extract_dir)):
    if fname.endswith(".jpg"):
        image_path = os.path.join(extract_dir, fname)
        all_data.extend(extract_data(image_path))

# --- SALVATAGGIO SU CSV ---
df = pd.DataFrame(all_data, columns=["Date", "Value1", "Value2", "Value3"])
df.to_csv(output_csv, index=False)

print(f"Dati salvati in {output_csv}")
