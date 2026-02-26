import os
import ollama
import base64

def perform_ocr_with_llama(folder_path, model="llama3.2-vision"):
    """
    Performs OCR on all images in the folder using Llama vision models and saves extracted text.
    The model is expected to handle blur and maintain text order.
    """
    image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg')) and f.startswith("media_")]
    extracted_texts = []

    if not image_files:
        print(f"  No images found in {folder_path} for OCR.")
        return ""

    for img_file in sorted(image_files):
        img_path = os.path.join(folder_path, img_file)
        print(f"  Performing Llama OCR on {img_file}...")
        
        try:
            # We use ollama.chat with the image
            response = ollama.chat(
                model=model,
                messages=[{
                    'role': 'user',
                    'content': 'Extract all text from this image precisely, including details from blurry areas, and maintain the original reading order.',
                    'images': [img_path]
                }]
            )
            
            text = response['message']['content'].strip()
            extracted_texts.append(f"--- Document: {img_file} ---\n{text}")
            
        except Exception as e:
            print(f"  Llama OCR failed for {img_file}: {e}")

    full_text = "\n\n".join(extracted_texts)
    
    if full_text:
        # Saving to the specific filename requested by user
        output_file = os.path.join(folder_path, "ocr_performed.txt")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(full_text)
        print(f"  OCR results saved to {output_file}")
        return full_text
    
    return ""

if __name__ == "__main__":
    # Example usage for testing
    import sys
    if len(sys.argv) > 1:
        perform_ocr_with_llama(sys.argv[1])
