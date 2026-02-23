📄 Gmail Unread Mail Extraction Bot

Scope:
Open Gmail (headed Chrome), detect unread emails from past 24 hours, extract full content (text + images), and store each email in a structured folder.

Nothing more. Nothing less.

1️⃣ System Overview
Stack

Language: Python

Browser Automation: Playwright or Selenium

Browser Mode: Headed Chrome

Output: Local filesystem

2️⃣ High-Level Workflow
Start
 │
 │
 ├── Launch Chrome (headed)
 │
 ├── Open Gmail
 │
 ├── Login (manual or automated)
 │
 ├── Wait for inbox to fully load
 │
 ├── Identify unread emails
 │
 ├── Filter unread emails from last 24 hours
 │
 ├── For each valid email:
 │      ├── Open email
 │      ├── Extract text content
 │      ├── Extract embedded images/media
 │      ├── Create folder: mail_[i]
 │      ├── Save content.txt
 │      ├── Save media_[i].png
 │      └── Return to inbox
 │
 └── End
3️⃣ Detailed Step-by-Step Workflow
🔹 Step 1: Launch Browser
Action

Launch Chrome in headed mode

Disable automation detection if needed

Requirements

Set user agent if necessary

Optionally use persistent user profile

🔹 Step 2: Open Gmail
URL
https://mail.google.com
Wait Conditions

Wait for inbox container to load

Ensure email list is rendered

🔹 Step 3: Identify Unread Emails
Gmail Characteristics

Unread emails usually:

Have bold subject text

Contain aria-label or class markers

Often contain “Unread” indicator in DOM

Extract:

Email row element

Timestamp

Unread status

🔹 Step 4: Filter Emails from Last 24 Hours
Logic

For each unread email:

Extract timestamp (e.g., “2:15 PM”, “Yesterday”, date string)

Convert to datetime

Compare against:

current_time - 24 hours

Keep only emails within this range

🔹 Step 5: Process Each Email

Loop through filtered emails.

🔹 Step 5.1: Open Email

Click email row

Wait for email body container to load

🔹 Step 5.2: Extract Text Content
Target

Main email body container.

Extract:

Sender name

Subject

Body text

Any visible structured content

Output

Create:

mail_[i]/
    content.txt

content.txt should contain:

Subject: ...
Sender: ...
Date: ...
Body:
<full extracted text>
🔹 Step 5.3: Extract Images / Media
Identify:

<img> tags inside email body

Inline images

Attachments (if rendered inline)

For each image:

Get image source URL or base64 data

Download or decode

Save inside:

mail_[i]/
    media_[1].png
    media_[2].png
    ...

Naming convention:

media_[index].png
🔹 Step 5.4: Folder Structure

For email number i:

mail_[i]/
    content.txt
    media_[1].png
    media_[2].png
    ...

Example:

mail_1/
    content.txt
    media_1.png

mail_2/
    content.txt
    media_1.png
    media_2.png
🔹 Step 5.5: Return to Inbox

Navigate back

Wait for inbox reload

Continue loop

4️⃣ Data Handling Rules

Overwrite existing mail_[i] if re-run

Preserve raw extracted text (no formatting modification)

Save images in PNG format only

5️⃣ Error Handling

Minimum handling:

If email fails to load → skip

If no images → only create content.txt

If extraction fails → log error and continue

6️⃣ Execution Flow Summary
Step	Description
1	Launch headed Chrome
2	Open Gmail
3	Detect unread emails
4	Filter last 24 hours
5	Open each email
6	Extract text
7	Extract images
8	Save to structured folder