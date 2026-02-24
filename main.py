import os
import sys
from extractor import GmailExtractor

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
                    
                    from llm_extractor import extract_insurance_info, classify_ocr_documents
                    from ocr_processor import perform_ocr
                    import json
                    
                    # 1. Structured Data Extraction from Body
                    extracted_data = extract_insurance_info(text, model="llama3")
                    json_path = os.path.join(folder_name, "extracted_data.json")
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(extracted_data, f, indent=2)
                    print(f"  Stored structured data in {json_path}")

                    # 2. OCR Step for Images
                    print(f"  Starting OCR for images in {folder_name}...")
                    ocr_text = perform_ocr(folder_name)
                    
                    # 3. Document Classification Step
                    if ocr_text:
                        print(f"  Classifying OCR documents for {folder_name}...")
                        classified_docs = classify_ocr_documents(ocr_text, model="llama3")
                        for doc_name, doc_content in classified_docs.items():
                            doc_path = os.path.join(folder_name, f"{doc_name}.txt")
                            with open(doc_path, "w", encoding="utf-8") as f:
                                f.write(doc_content)
                            print(f"    Saved classified document: {doc_path}")
                
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
