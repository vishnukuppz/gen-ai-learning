import time
import re
import os
import pandas as pd
from playwright.sync_api import sync_playwright
from datetime import datetime


def read_contacts(file_path="contacts.xlsx"):
    """
    Reads contacts from an Excel file with columns: Name, Phone, Message.
    Returns a list of dictionaries containing contact details.
    """
    create_sample = False
    if not os.path.exists(file_path):
        create_sample = True
    else:
        try:
            df = pd.read_excel(file_path, dtype=str, engine="openpyxl")
        except Exception as e:
            print(f"File '{file_path}' corrupted or unreadable ({e}). Re-creating sample...")
            create_sample = True

    if create_sample:
        sample_data = pd.DataFrame([
            {"Name": "Prachana", "Phone": "+919843230669", "Message": "Hello Prachana!, nan our bot-tu"},
            {"Name": "Durga", "Phone": "+916380485834", "Message": "Hello Durga!, nan our bot-tu"},
        ])
        sample_data.to_excel(file_path, index=False, engine="openpyxl")
        df = pd.read_excel(file_path, dtype=str, engine="openpyxl")

    contacts = []
    for _, row in df.iterrows():
        name = str(row.get("Name", "")).strip() if pd.notna(row.get("Name")) else ""
        phone = str(row.get("Phone", "")).strip() if pd.notna(row.get("Phone")) else ""
        
        # Format phone number to ensure country code '+' prefix
        if phone and not phone.startswith("+"):
            phone = "+" + phone

        message = str(row.get("Message", "")).strip() if pd.notna(row.get("Message")) else ""

        if name or phone:
            contacts.append({
                "name": name,
                "phone": phone,
                "message": message
            })
    print(f"Successfully loaded {len(contacts)} contacts from {file_path}")
    return contacts


def search_and_select_contact(page, name):
    print(f"\n--- Searching for contact: '{name}' ---")
    # 1. Locate search input box
    search_box = page.locator(
        "div[contenteditable='true'][data-tab='3'], "
        "div[contenteditable='true'][title='Search input box'], "
        "[aria-label='Search input box or start a new chat'], "
        "[aria-label='Search or start a new chat']"
    ).first
    
    search_box.wait_for(state="visible", timeout=10000)
    search_box.click()
    time.sleep(0.5)
    
    # Clear existing search input using keyboard shortcuts (Meta+A on macOS)
    page.keyboard.press("Meta+A")
    page.keyboard.press("Backspace")
    time.sleep(0.5)
    
    # Type contact name
    page.keyboard.type(name, delay=100)
    time.sleep(2)  # Allow time for search results to render
    
    # 2. Select first matching list item in #pane-side
    first_result = page.locator(
        "#pane-side div[role='listitem'], "
        "#pane-side [data-testid='cell-frame-container'], "
        "#pane-side div[role='gridcell']"
    ).first
    
    print(f"Waiting for contact '{name}' in search results list...")
    first_result.wait_for(state="visible", timeout=10000)
    time.sleep(1)
    print(f"Clicking first search result item for '{name}'...")
    first_result.click()
    time.sleep(1.5)


def type_message(page, message):
    if not message:
        print("Message content is empty, skipping message dispatch.")
        return

    print(f"Typing message: '{message}'...")
    # Locate message input box in active chat footer
    message_box = page.locator(
        "footer div[contenteditable='true'], "
        "div[contenteditable='true'][data-tab='10'], "
        "[aria-label='Type a message']"
    ).first
    
    message_box.wait_for(state="visible", timeout=10000)
    message_box.click()
    time.sleep(0.5)
    
    # Type message text and press Enter
    page.keyboard.type(message, delay=50)
    time.sleep(0.5)
    page.keyboard.press("Enter")
    print("✓ Message sent successfully!")
    time.sleep(1)


def get_last_messages(page, count=3) -> list[str]:
    """
    Extracts the last 'count' messages from the active chat window on WhatsApp Web.
    Returns a list of strings containing message texts.
    """
    time.sleep(1)  # Allow DOM to settle after sending
    selectors = [
        "#main .copyable-text span.selectable-text",
        "#main [data-testid='msg-container'] span.selectable-text",
        "#main div.message-in span.selectable-text, #main div.message-out span.selectable-text",
        "#main span.selectable-text"
    ]
    
    messages = []
    for selector in selectors:
        elements = page.locator(selector).all_text_contents()
        cleaned = [txt.strip() for txt in elements if txt.strip()]
        if cleaned:
            messages = cleaned
            break

    last_messages = messages[-count:] if len(messages) >= count else messages
    return last_messages


def main():
    # 1. Read contacts from Excel file
    contacts = read_contacts("contacts.xlsx")
    print("Contacts loaded:", contacts)

    # 2. Setup persistent Chrome session
    user_data_dir = os.path.abspath("whatsapp_session")
    print(f"Using persistent Chrome session directory: {user_data_dir}")

    with sync_playwright() as p:
        print("Launching Google Chrome...")
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                slow_mo=1000,
                channel="chrome"
            )
        except Exception as e:
            print(f"Chrome channel unavailable ({e}), launching default Chromium...")
            context = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                slow_mo=1000
            )

        page = context.pages[0] if context.pages else context.new_page()

        print("Navigating to WhatsApp Web...")
        page.goto("https://web.whatsapp.com")
        time.sleep(2)

        dashboard_selector = "#pane-side, [data-testid='chat-list'], [aria-label='Chat list']"

        print("Checking session status...")
        try:
            page.wait_for_selector(dashboard_selector, timeout=5000)
            print("✓ Persistent session active! Automatically logged into WhatsApp Web.")
        except Exception:
            print("\n=======================================================")
            print(" No active session found.                              ")
            print(" Please scan the QR code in Chrome to log in once.     ")
            print(" Your session will be saved automatically for future runs. ")
            print("=======================================================\n")
            page.wait_for_selector(dashboard_selector, timeout=0)
            print("✓ Login successful! Session saved for future runs.")

        page.screenshot(path="whatsapp_dashboard.png")
        print(f"Dashboard active! Current URL: {page.url}")

        # Iterate through loaded contacts, send message, and fetch last 3 messages
        for contact in contacts:
            search_and_select_contact(page, contact["name"])
            type_message(page, contact["message"])
            
            # Retrieve last 3 messages from chat window, store in variable, and print
            recent_messages = get_last_messages(page, count=3)
            print(f"Last 3 messages in chat with '{contact['name']}': {recent_messages}")


if __name__ == "__main__":
    main()
