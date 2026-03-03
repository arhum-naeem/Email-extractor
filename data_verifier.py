import json
import os

def cross_verify_and_merge(body_data, ocr_data):
    """
    Merges data from email body and OCR results.
    Performs simple cross-verification.
    """
    merged_data = body_data.copy()

    if not ocr_data:
        return merged_data

    for category, fields in ocr_data.items():
        if category not in merged_data:
            merged_data[category] = {}
        
        if isinstance(fields, dict):
            for key, val in fields.items():
                if not val or val == "N/A":
                    continue
                
                existing_val = merged_data[category].get(key)
                
                if not existing_val or existing_val == "N/A":
                    # Fill missing data from OCR
                    merged_data[category][key] = val
                elif existing_val.lower() != val.lower():
                    # Cross-verification mismatch
                    # For now, we'll prefer OCR data for critical fields like CNIC/License
                    # but we'll log it.
                    print(f"  [Verification] Mismatch in {category}.{key}: Body='{existing_val}', OCR='{val}'. Preferring OCR.")
                    merged_data[category][key] = val
                else:
                    # Verified match
                    print(f"  [Verification] Match found for {category}.{key}: '{val}'")

    return merged_data

def update_root_user_data(final_data, root_path="user_data.json"):
    """Updates the root user_data.json with the verified data."""
    try:
        # Validate that final_data is not empty or None
        if not final_data:
            print(f"  Warning: Attempted to write empty data to {root_path}")
            return
        
        # Check if it's an error object
        if "error" in final_data:
            print(f"  Warning: Attempted to write error data to {root_path}: {final_data['error']}")
            return
        
        with open(root_path, "w", encoding="utf-8") as f:
            json.dump(final_data, f, indent=2, ensure_ascii=False)
        print(f"  Successfully updated verified data in {root_path}")
        
        # Verify the file was written correctly
        with open(root_path, "r", encoding="utf-8") as f:
            written_data = json.load(f)
            if not written_data:
                print(f"  Error: File {root_path} was written but is empty!")
            else:
                print(f"  Verified: {root_path} contains {len(written_data)} categories")
    except Exception as e:
        print(f"  Error updating root user_data.json: {e}")
        import traceback
        traceback.print_exc()
