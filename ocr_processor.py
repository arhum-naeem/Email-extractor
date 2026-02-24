import os
import easyocr
from PIL import Image
import numpy as np

def perform_ocr(folder_path):
    """
    Performs OCR on all images in the folder and saves the result to OCR.txt.
    Returns the combined text.
    """
    reader = easyocr.Reader(['en']) # Add other languages if needed
    
    image_files = [f for f in os.listdir(folder_path) if f.startswith("media_")]
    combined_text = []

    for img_file in sorted(image_files):
        img_path = os.path.join(folder_path, img_file)
        print(f"  Performing OCR on {img_file}...")
        try:
            # easyocr can take the path directly
            results = reader.readtext(img_path, detail=0)
            text = " ".join(results)
            combined_text.append(f"--- Document: {img_file} ---\n{text}")
        except Exception as e:
            print(f"  OCR failed for {img_file}: {e}")

    full_ocr_text = "\n\n".join(combined_text)
    
    if full_ocr_text:
        ocr_file_path = os.path.join(folder_path, "OCR.txt")
        with open(ocr_file_path, "w", encoding="utf-8") as f:
            f.write(full_ocr_text)
        return full_ocr_text
    
    return ""
