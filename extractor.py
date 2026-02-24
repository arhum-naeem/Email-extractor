import os
import base64
import time
from playwright.sync_api import sync_playwright
from utils import setup_folder, save_content, is_within_24_hours

class GmailExtractor:
    def __init__(self, user_data_dir):
        self.user_data_dir = user_data_dir
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def start(self):
        self.playwright = sync_playwright().start()
        # Headed Chrome with persistent context
        self.context = self.playwright.chromium.launch_persistent_context(
            self.user_data_dir,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        self.page = self.context.pages[0] if self.context.pages else self.context.new_page()

    def login(self):
        self.page.goto("https://mail.google.com")
        print("Checking login status...")
        # Wait for inbox to load or login screen
        try:
            # Selector for the 'Compose' button or inbox rows, which indicates we are logged in
            self.page.wait_for_selector(".T-I.T-I-KE.L3", timeout=15000) 
            print("Already logged in and inbox loaded.")
        except:
            print("Please log in manually in the browser window.")
            # Increased timeout for manual login
            self.page.wait_for_selector(".T-I.T-I-KE.L3", timeout=300000) 

    def get_unread_emails_from_last_24h(self):
        print("Identifying unread emails from the last 24 hours...")
        
        # Ensure we are in the 'Primary' tab or at least seeing emails
        # Unread rows in Gmail usually have the class 'zE'
        # We'll use a more general selector to be safe
        self.page.wait_for_selector("tr.zE, tr.zA", timeout=20000)
        
        rows = self.page.locator("tr.zE").all()
        print(f"Found {len(rows)} total unread emails in the current view.")
        
        valid_emails = []
        for i, row in enumerate(rows):
            try:
                # Extract timestamp
                # Gmail's timestamp is usually in a <span> inside a <td> with class 'xW'
                date_element = row.locator("td.xW span")
                if date_element.count() > 0:
                    # 'title' attribute often contains the full date/time
                    date_str = date_element.first.get_attribute("title") or date_element.first.inner_text()
                    print(f"  Email {i+1} date: {date_str}")
                    if is_within_24_hours(date_str):
                        valid_emails.append(row)
                else:
                    print(f"  Email {i+1}: Could not find date element.")
            except Exception as e:
                print(f"  Error checking email {i+1}: {e}")
        
        print(f"Found {len(valid_emails)} unread emails from the last 24 hours.")
        return valid_emails

    def process_email(self, row, index):
        folder_name = f"mail_{index}"
        setup_folder(folder_name)
        
        # Click to open
        row.click()
        self.page.wait_for_selector("div.h7", timeout=20000) # Email body container
        
        # Extract metadata
        subject = self.page.locator("h2.hP").inner_text()
        sender = self.page.locator("span.gD").first.inner_text()
        date_full = self.page.locator("span.g3").first.get_attribute("title")
        
        # Extract body text
        body_locator = self.page.locator("div.a3s.aiL")
        body_text = body_locator.inner_text()
        
        save_content(folder_name, subject, sender, date_full, body_text)
        
        # Extract images (Refined to target only attachments/inline images)
        # We target the body and the attachment area if it exists
        attachment_area = self.page.locator("div.hq.gt")
        
        all_images = []
        # Inline images in body
        all_images.extend(body_locator.locator("img").all())
        # Images in attachment area
        if attachment_area.count() > 0:
            all_images.extend(attachment_area.locator("img").all())

        extracted_count = 0
        for i, img in enumerate(all_images):
            try:
                # Filter out small UI icons (usually < 30px)
                box = img.bounding_box()
                if box and (box['width'] < 30 or box['height'] < 30):
                    continue

                src = img.get_attribute("src")
                if not src: continue
                
                # If it's base64
                if src.startswith("data:image/"):
                    header, data = src.split(",", 1)
                    ext = header.split("/")[1].split(";")[0]
                    img_data = base64.b64decode(data)
                    file_name = f"media_{extracted_count + 1}.{ext}"
                    with open(os.path.join(folder_name, file_name), "wb") as f:
                        f.write(img_data)
                    extracted_count += 1
                else:
                    # Take screenshot of the image element
                    file_name = f"media_{extracted_count + 1}.png"
                    img.screenshot(path=os.path.join(folder_name, file_name))
                    extracted_count += 1
            except Exception as e:
                print(f"Failed to extract image {i+1}: {e}")
        
        # Return to inbox
        self.page.locator("div.T-I.J-J5-Ji.lS.T-I-ax7.L3").click() # "Back to Inbox" button
        self.page.wait_for_selector("tr.zE", timeout=10000)

    def close(self):
        if self.context:
            self.context.close()
        if self.playwright:
            self.playwright.stop()
