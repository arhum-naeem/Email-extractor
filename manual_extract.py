"""
Manual extraction script to populate user_data.json from existing mail_1 folder.
This bypasses the Gmail automation and directly extracts from saved content.
"""
import os
import json
from llm_extractor import extract_insurance_info
from ocr_processor import perform_gemini_ocr
from data_verifier import cross_verify_and_merge, update_root_user_data

def manual_extract():
    print("=" * 60)
    print("MANUAL EXTRACTION FROM mail_1 FOLDER")
    print("=" * 60)
    
    folder_name = "mail_1"
    
    if not os.path.exists(folder_name):
        print(f"Error: {folder_name} folder not found!")
        return
    
    # Check for content file
    content_file = os.path.join(folder_name, "content.txt")
    if not os.path.exists(content_file):
        print(f"Error: {content_file} not found!")
        return
    
    print(f"\n1. Reading email content from {content_file}...")
    with open(content_file, "r", encoding="utf-8") as f:
        text = f.read()
    
    # LLM Extraction from body
    print("\n2. Extracting structured data using LLM...")
    print("  Note: Using 'llama2:latest' model")
    body_extracted_data = extract_insurance_info(text, model="llama2:latest")
    
    if not body_extracted_data:
        print("  ERROR: No data extracted from body!")
        return
    elif "error" in body_extracted_data:
        print(f"  ERROR: {body_extracted_data['error']}")
        return
    else:
        print(f"  ✓ Successfully extracted {len(body_extracted_data)} categories")
        print(f"  Categories: {', '.join(body_extracted_data.keys())}")
    
    # Save body extraction result
    body_json_path = os.path.join(folder_name, "body_extracted_data.json")
    with open(body_json_path, "w", encoding="utf-8") as f:
        json.dump(body_extracted_data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Saved body extraction to {body_json_path}")
    
    # OCR Extraction from images
    print("\n3. Performing OCR on images...")
    ocr_extracted_data = perform_gemini_ocr(folder_name)
    
    if not ocr_extracted_data:
        print("  ⚠ No data extracted from images (this is OK)")
    else:
        print(f"  ✓ Successfully extracted {len(ocr_extracted_data)} categories from OCR")
    
    # Cross-verify and merge
    print("\n4. Cross-verifying and merging data...")
    final_verified_data = cross_verify_and_merge(body_extracted_data, ocr_extracted_data)
    
    if not final_verified_data:
        print("  ERROR: Final merged data is empty!")
        return
    elif "error" in final_verified_data:
        print(f"  ERROR: Final data contains error: {final_verified_data['error']}")
        return
    else:
        print(f"  ✓ Merged data has {len(final_verified_data)} categories")
    
    # Save individual verified result
    verified_json_path = os.path.join(folder_name, "verified_extracted_data.json")
    with open(verified_json_path, "w", encoding="utf-8") as f:
        json.dump(final_verified_data, f, indent=2, ensure_ascii=False)
    print(f"  ✓ Saved verified data to {verified_json_path}")
    
    # Update root user_data.json
    print("\n5. Updating root user_data.json...")
    update_root_user_data(final_verified_data)
    
    # Final verification
    print("\n6. Verifying user_data.json...")
    if os.path.exists("user_data.json"):
        with open("user_data.json", "r", encoding="utf-8") as f:
            user_data = json.load(f)
        
        if user_data:
            print(f"  ✓ SUCCESS! user_data.json populated with {len(user_data)} categories:")
            for category in user_data.keys():
                print(f"    - {category}")
            
            # Display summary
            print("\n" + "=" * 60)
            print("EXTRACTION COMPLETE!")
            print("=" * 60)
            print(f"\nPolicyholder: {user_data.get('personal_info', {}).get('full_legal_name', 'N/A')}")
            print(f"Vehicle: {user_data.get('vehicle_info', {}).get('make', 'N/A')} {user_data.get('vehicle_info', {}).get('model', 'N/A')}")
            print(f"Coverage: {', '.join(user_data.get('coverage_selection', {}).get('coverage_types', []))}")
        else:
            print("  ERROR: user_data.json is empty!")
    else:
        print("  ERROR: user_data.json was not created!")

if __name__ == "__main__":
    manual_extract()
