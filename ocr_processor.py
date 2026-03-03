import os
from google import genai
from PIL import Image
import json
from dotenv import load_dotenv

# Load environment variables (for GEMINI_API_KEY)
load_dotenv()

def perform_gemini_ocr(folder_path):
    """
    Performs OCR on all images in the folder using Google Gemini API (google-genai SDK).
    Returns a combined dictionary of extracted data and full text.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("  Error: GEMINI_API_KEY not found in environment variables.")
        return None

    client = genai.Client(api_key=api_key)
    model_id = "gemini-2.5-flash"

    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    if not image_files:
        return None

    extracted_results = []
    combined_full_text = []

    prompt = """
    Extract all information from this document image. 
    Focus on insurance-related details.
    Return the result strictly as a valid JSON object with two top-level keys:
    1. 'structured_data': A JSON object following this exact schema (use null for missing):
       {
         "personal_info": {"full_legal_name": null, "cnic_or_id": null, "date_of_birth": null, "gender": null, "marital_status": null, "occupation": null, "contact_phone": null, "contact_email": null, "residential_address": null},
         "driving_history": {"driving_license_number": null, "license_issue_date": null, "license_expiry_date": null, "years_of_experience": null, "past_accidents": null, "traffic_violations": null, "previous_insurance_claims": null, "claim_history_details": null},
         "vehicle_info": {"make": null, "model": null, "year_of_manufacture": null, "engine_number": null, "chassis_number": null, "registration_number": null, "fuel_type": null, "engine_capacity_cc": null, "vehicle_value": null, "modifications": null, "usage_type": null},
         "coverage_selection": {"coverage_types": []},
         "financial_info": {"payment_method": null, "installment_or_full": null, "bank_details": null, "no_claim_bonus_eligibility": null},
         "risk_factors": {"parking_location": null, "city_of_registration": null, "anti_theft_devices": null, "annual_mileage": null, "primary_driver_type": null},
         "legal_doc": {"documents_provided": []}
       }
    2. 'full_text': A string containing all raw text extracted from the image.

    Return ONLY the JSON.
    """

    for img_file in sorted(image_files):
        img_path = os.path.join(folder_path, img_file)
        print(f"  Performing Gemini OCR on {img_file}...")
        try:
            img = Image.open(img_path)
            response = client.models.generate_content(
                model=model_id,
                contents=[prompt, img]
            )
            
            # Clean up response to get JSON
            content = response.text.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            data = json.loads(content)
            extracted_results.append(data)
            combined_full_text.append(f"--- Document: {img_file} ---\n{data.get('full_text', '')}")
        except Exception as e:
            print(f"  Gemini OCR failed for {img_file}: {e}")

    # Merge all extracted structured data
    final_structured_data = {}
    for res in extracted_results:
        struct = res.get("structured_data", {})
        for category, fields in struct.items():
            if category not in final_structured_data:
                final_structured_data[category] = {}
            if isinstance(fields, dict):
                for k, v in fields.items():
                    if v and v != "N/A" and v != "null" and v is not None:
                        final_structured_data[category][k] = v

    full_ocr_text = "\n\n".join(combined_full_text)
    
    if full_ocr_text or final_structured_data:
        ocr_file_path = os.path.join(folder_path, "Gemini_OCR.txt")
        with open(ocr_file_path, "w", encoding="utf-8") as f:
            f.write(full_ocr_text)
        
        json_path = os.path.join(folder_path, "gemini_extracted_data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(final_structured_data, f, indent=2)
            
        return final_structured_data
    
    return None

if __name__ == "__main__":
    # Test
    perform_gemini_ocr("mail_1")
    pass
