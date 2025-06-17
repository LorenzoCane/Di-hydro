
import os
import re
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pandas as pd


def enhance_image_for_ocr(image_path):
    img = Image.open(image_path).convert('L')  # grigio
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)
    img = img.filter(ImageFilter.SHARPEN)
    return img

def extract_protok_data(image_path):
    img = enhance_image_for_ocr(image_path)
    text = pytesseract.image_to_string(img, lang="eng")

    date_match = re.search(r"Protok_(\d{2})\.(\d{2})\.(\d{4})", os.path.basename(image_path))
    if not date_match:
        return []
    date_str = f"{date_match.group(3)}-{date_match.group(2)}-{date_match.group(1)}"

    rows = []
    for line in text.splitlines():
        match = re.findall(r'\d+\.\d{1,2}', line)
        if len(match) >= 2:
            rows.append([date_str] + match[:3])  # al massimo 3 valori
    return rows