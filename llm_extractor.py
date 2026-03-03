import json
import ollama

def extract_insurance_info(text, model="llama3"):
    """
    Uses Ollama to extract structured insurance information from email text.
    """
    prompt = """
    Extract the following insurance-related information from the email text provided below. 
    Return the result strictly as a valid JSON object. 
    If a field is not found, use "N/A" as the value.

    Schema (snake_case keys):
    - personal_info: {full_legal_name, cnic_or_id, date_of_birth, gender, marital_status, occupation, contact_phone, contact_email, residential_address}
    - driving_history: {driving_license_number, license_issue_date, license_expiry_date, years_of_experience, past_accidents, traffic_violations, previous_insurance_claims, claim_history_details}
    - vehicle_info: {make, model, year_of_manufacture, engine_number, chassis_number, registration_number, fuel_type, engine_capacity_cc, vehicle_value, modifications, usage_type}
    - coverage_selection: {coverage_types: []}
    - financial_info: {payment_method, installment_or_full, bank_details, no_claim_bonus_eligibility}
    - risk_factors: {parking_location, city_of_registration, anti_theft_devices, annual_mileage, primary_driver_type}
    - legal_doc: {documents_provided: []}

    Email Text:
    \"""
    """ + text + """
    \""

    Strict JSON Output:
    """

    try:
        response = ollama.generate(model=model, prompt=prompt)
        # Attempt to find JSON block in case the LLM adds chatter
        content = response['response'].strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)
    except Exception as e:
        print(f"Error during LLM extraction: {e}")
        return {"error": str(e), "raw_response": content if 'content' in locals() else None}

def classify_ocr_documents(ocr_text, model="llama3"):
    """
    Uses Ollama to identify distinct documents in OCR text and extract their content.
    Returns a dictionary of {doc_name: content}.
    """
    if not ocr_text:
        return {}

    prompt = f"""
    Below is a text result from an OCR process on several images attached to an email.
    The text might contain multiple legal or personal documents (e.g., CNIC, Driving License, Vehicle Registration, Insurance Policy).
    
    Your task is to:
    1. Identify each distinct document found in the text.
    2. Extract the relevant text for each document.
    3. Return the result strictly as a valid JSON object where keys are the document names (slugified, e.g., "cnic", "driving_license") and values are the extracted text for that specific document.
    
    If multiple documents of the same type are found, merge them or index them (e.g., "cnic_front", "cnic_back").
    
    OCR Text:
    \"\"\"
    {ocr_text}
    \"\"\"
    
    Strict JSON Output:
    """

    try:
        response = ollama.generate(model=model, prompt=prompt)
        content = response['response'].strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        return json.loads(content)
    except Exception as e:
        print(f"Error during document classification: {e}")
        return {}

if __name__ == "__main__":
    # Test with sample text
    sample_text = "My name is John Doe, CNIC 12345-6789012-3. I drive a 2022 Toyota Corolla. I want comprehensive coverage."
    result = extract_insurance_info(sample_text)
    print(json.dumps(result, indent=2))
