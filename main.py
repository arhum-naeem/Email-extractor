import os
import sys
import json
from extractor import GmailExtractor
from llm_extractor import extract_insurance_info
from ocr_processor import perform_gemini_ocr
from data_verifier import cross_verify_and_merge, update_root_user_data

def main():
    # Path for browser profile to keep login session
    user_data_dir = os.path.join(os.getcwd(), "user_data")
    
    extractor = GmailExtractor(user_data_dir)
    
    try:
        extractor.start()
        extractor.login()
        
        unread_emails = extractor.get_unread_emails_from_last_24h()
        
        if not unread_emails:
            print("No unread emails from the last 24 hours found.")
            return

        for i, row in enumerate(unread_emails):
            try:
                print(f"Processing email {i+1} of {len(unread_emails)}...")
                folder_name = f"mail_{i+1}"
                extractor.process_email(row, i+1)
                
                # LLM Extraction Step
                content_file = os.path.join(folder_name, "content.txt")
                if os.path.exists(content_file):
                    print(f"  Extracting structured data using LLM for {folder_name}...")
                    with open(content_file, "r", encoding="utf-8") as f:
                        text = f.read()
                    
                    # 1. Body Data Extraction (Ollama)
                    print(f"  Extracting structured data from body using LLM for {folder_name}...")
                    body_extracted_data = extract_insurance_info(text, model="llama2:latest")
                    
                    # Debug: Check what was extracted
                    if not body_extracted_data:
                        print(f"  Warning: No data extracted from email body!")
                    elif "error" in body_extracted_data:
                        print(f"  Error in body extraction: {body_extracted_data['error']}")
                    else:
                        print(f"  Successfully extracted {len(body_extracted_data)} categories from body")
                    
                    # 2. Gemini OCR for Images
                    print(f"  Starting Gemini OCR for images in {folder_name}...")
                    ocr_extracted_data = perform_gemini_ocr(folder_name)
                    
                    if not ocr_extracted_data:
                        print(f"  Warning: No data extracted from images in {folder_name}.")
                    else:
                        print(f"  Successfully extracted {len(ocr_extracted_data)} categories from OCR")
                    
                    # 3. Cross-Verify and Merge
                    print(f"  Verifying and merging data for {folder_name}...")
                    final_verified_data = cross_verify_and_merge(body_extracted_data, ocr_extracted_data)
                    
                    # Debug: Check final data before saving
                    if not final_verified_data:
                        print(f"  ERROR: Final verified data is empty!")
                    elif "error" in final_verified_data:
                        print(f"  ERROR: Final data contains error: {final_verified_data['error']}")
                    else:
                        print(f"  Final verified data has {len(final_verified_data)} categories")
                    
                    # 4. Save individual results
                    json_path = os.path.join(folder_name, "verified_extracted_data.json")
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(final_verified_data, f, indent=2)
                    print(f"  Stored verified data in {json_path}")

                    # 5. Update root user_data.json
                    update_root_user_data(final_verified_data)

                    # 6. Optional Document Classification
                    # (Remaining classification steps if needed...)
                
            except Exception as e:
                print(f"Error processing email {i+1}: {e}")
                # Try to return to inbox if we're lost
                try:
                    extractor.page.goto("https://mail.google.com")
                except:
                    pass
                
        print("Extraction complete.")
        
    except KeyboardInterrupt:
        print("\nStopping bot...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        extractor.close()

if __name__ == "__main__":
    main()
