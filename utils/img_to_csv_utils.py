"""
    OCR-based Data Extractor

    This module provides functionality to extract hourly water discharge data from scanned 
    protocol images using OCR (Optical Character Recognition). It uses Tesseract OCR to read 
    text from enhanced images and applies regular expressions to parse numerical discharge values.
    Be AWARE OF SOME MALFUNCTIONALITY OF THE FUNCTIONS AND ALWAYS CHECK SOME RANDOM RESULTS!

    Enhancer parameters can be adapted to the specific use case 

    Functions:

    - enhance_image_for_ocr: Enhances contrast and sharpness of an image to improve OCR accuracy.
    - extract_protok_data: Extracts hourly discharge values and associated date from a scanned 
      protocol image.

    Author: Lorenzo Cane - DBL E&E Area Consultant  
    Last modified: 20/06/2025
"""
import os
import re
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import pandas as pd


def enhance_image_for_ocr(image_path):
    """
        Enhance image contrast and sharpness for better OCR performance.

        Parameters:
        -----------
        image_path : str
            Path to the image file.

        Returns:
        --------
        PIL.Image.Image
            Processed grayscale image optimized for OCR.
    """
    img = Image.open(image_path).convert('L')  # grigio
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)
    img = img.filter(ImageFilter.SHARPEN)
    return img

def extract_protok_data(image_path):
    """
        Extract hourly discharge data from a protocol image using OCR.

        Parameters:
        -----------
        image_path : str
            Path to the scanned protocol image (filename must include date in format Protok_DD.MM.YYYY).

        Returns:
        --------
        list of lists
            A list of rows, each containing [date (YYYY-MM-DD), value1, value2, value3]. 
        
        Only the first 24 valid rows are returned to exclude daily summaries.
    """
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
            rows.append([date_str] + match[:3])  # max 3 value per row

    #Limit range to the 24 hourly data excluding last line (daily summary)
    return rows[:24]