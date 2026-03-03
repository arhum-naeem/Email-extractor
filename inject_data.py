import json
import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def inject_data(json_file, url="http://localhost:5173"):
    # Load data
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found.")
        return

    with open(json_file, 'r') as f:
        data = json.load(f)

    # Selenium Setup (Headed mode)
    chrome_options = Options()
    # chrome_options.add_argument("--headless") # Headed mode as requested
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        print(f"Navigating to {url}...")
        driver.get(url)
        
        # Wait for form to load
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "extraction-form")))
        print("Form loaded. Starting tabbed injection...")

        def switch_tab(tab_id):
            print(f"Switching to tab: {tab_id}")
            tab_btn = wait.until(EC.element_to_be_clickable((By.ID, f"tab-btn-{tab_id}")))
            tab_btn.click()
            time.sleep(0.5) # Short delay for tab transition

        # 1. Personal Info
        switch_tab("personal")
        personal = data.get("personal_info", {})
        fields = [
            "full_legal_name", "cnic_or_id", "date_of_birth", 
            "occupation", "contact_phone", "contact_email"
        ]
        for field in fields:
            val = personal.get(field)
            if val:
                driver.find_element(By.NAME, f"personal_info.{field}").send_keys(val)

        addr = personal.get("residential_address")
        if addr:
            driver.find_element(By.NAME, "personal_info.residential_address").send_keys(addr)

        for field in ["gender", "marital_status"]:
            val = personal.get(field)
            if val:
                driver.find_element(By.NAME, f"personal_info.{field}").send_keys(val)

        # 2. Driving History
        switch_tab("driving")
        history = data.get("driving_history", {})
        for field in ["driving_license_number", "license_issue_date", "years_of_experience", "past_accidents"]:
            val = history.get(field)
            if val:
                driver.find_element(By.NAME, f"driving_history.{field}").send_keys(val)

        # 3. Vehicle Info
        switch_tab("vehicle")
        vehicle = data.get("vehicle_info", {})
        for field in ["make", "model", "year_of_manufacture", "registration_number", "vehicle_value"]:
            val = vehicle.get(field)
            if val:
                driver.find_element(By.NAME, f"vehicle_info.{field}").send_keys(val)
        
        usage = vehicle.get("usage_type")
        if usage:
            driver.find_element(By.NAME, "vehicle_info.usage_type").send_keys(usage)

        # 4. Coverage Selection
        switch_tab("coverage")
        coverage = data.get("coverage_selection", {}).get("coverage_types", [])
        for item in coverage:
            try:
                cb = driver.find_element(By.CSS_SELECTOR, f"input[name='coverage_selection.coverage_types'][value='{item}']")
                if not cb.is_selected():
                    cb.click()
            except:
                print(f"Warning: Coverage option '{item}' not found.")

        # 5. Financial Info
        switch_tab("financial")
        finance = data.get("financial_info", {})
        pm = finance.get("payment_method")
        if pm:
            driver.find_element(By.NAME, "financial_info.payment_method").send_keys(pm)
        
        inst = finance.get("installment_or_full")
        if inst:
            driver.find_element(By.NAME, "financial_info.installment_or_full").send_keys(inst)

        # 6. Risk Factors
        switch_tab("risk")
        risk = data.get("risk_factors", {})
        for field in ["parking_location", "annual_mileage"]:
            val = risk.get(field)
            if val:
                driver.find_element(By.NAME, f"risk_factors.{field}").send_keys(val)

        # 7. Documents Provided
        switch_tab("docs")
        docs = data.get("legal_doc", {}).get("documents_provided", [])
        for doc in docs:
            try:
                cb = driver.find_element(By.CSS_SELECTOR, f"input[name='legal_doc.documents_provided'][value='{doc}']")
                if not cb.is_selected():
                    cb.click()
            except:
                print(f"Warning: Document option '{doc}' not found.")

        print("Injection complete. Submitting form...")
        # Since the submit button is in the footer and always visible in my new layout, we can click it anytime.
        submit_btn = driver.find_element(By.ID, "submit-extraction")
        submit_btn.click()

        # Wait for success message
        try:
            success_msg = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "status-success")))
            print(f"Success! Server response: {success_msg.text}")
            time.sleep(2) # Leave browser open for a moment to see success
        except:
            print("Timed out waiting for success message.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    inject_data("user_data.json")
