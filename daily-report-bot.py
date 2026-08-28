"""
Daily Report Bot - Automated macOS GUI Reporting Workflow
Week 1 - Day 3 Assignment

This script automates:
1. Launching Google Chrome via Spotlight
2. Navigating to the target website (Sample Document)
3. Copying page content to clipboard
4. Saving raw content to a local date-stamped text file
5. Formatting a 3-column summary row (Timestamp, Snippet, Comment)
6. Opening macOS Numbers, populating the spreadsheet, and saving the document
7. Taking a date-stamped screenshot
"""

import os
import time
import datetime
import pyautogui
import pyperclip

# ==============================================================================
# CONFIGURATION
# ==============================================================================
TARGET_URL = "https://documentero.com/templates/general-examples/document/sample-document/"
DEFAULT_COMMENT = "Good for outdoor activities"

CHROME_APP_NAME = "Google Chrome"
NUMBERS_APP_NAME = "Numbers"

# Delays (in seconds) for macOS UI animations and app launching
SPOTLIGHT_DELAY = 1.0
APP_LAUNCH_DELAY = 2.5
PAGE_LOAD_DELAY = 3.5
ACTION_DELAY = 0.5

# PyAutoGUI Safety Settings
pyautogui.PAUSE = 0.5 
pyautogui.FAILSAFE = True


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================
def open_spotlight():
    """Opens macOS Spotlight search using explicit hold + press command sequence."""
    pyautogui.keyDown('command')
    time.sleep(0.1)
    pyautogui.press('space')
    time.sleep(0.1)
    pyautogui.keyUp('command')
    time.sleep(SPOTLIGHT_DELAY)


def press_cmd_key(key: str):
    """Executes a Command + <key> shortcut with explicit key press holding."""
    pyautogui.keyDown('command')
    time.sleep(0.1)
    pyautogui.press(key)
    time.sleep(0.1)
    pyautogui.keyUp('command')


def open_app_via_spotlight(app_name: str, wait_seconds: float = APP_LAUNCH_DELAY):
    """Launches an application by searching in macOS Spotlight."""
    print(f"--> Opening Spotlight and launching {app_name}...")
    open_spotlight()
    pyautogui.typewrite(app_name, interval=0.1)
    pyautogui.press('enter')
    time.sleep(wait_seconds)


def navigate_in_browser(url: str):
    """Focuses the browser address bar and pastes the URL."""
    print(f"--> Navigating to {url}...")
    press_cmd_key('l')  # Focus address bar directly
    time.sleep(ACTION_DELAY)

    pyperclip.copy(url)
    press_cmd_key('v')  # Paste URL to avoid special character typos
    pyautogui.press('enter')
    time.sleep(PAGE_LOAD_DELAY)


def copy_webpage_content(start_x: int = 200, start_y: int = 650, end_x: int = 800, end_y: int = 900) -> str:
    """Selects a specific area on the web page using mouse drag and copies it to clipboard."""
    print(f"--> Selecting screen area from ({start_x}, {start_y}) to ({end_x}, {end_y}) via mouse drag...")
    
    # Move to starting point inside the web page content viewport (y >= 250 avoids Chrome tab/toolbar)
    pyautogui.moveTo(start_x, start_y)
    time.sleep(0.2)
    
    # Press mouse button down
    pyautogui.mouseDown(button='left')
    time.sleep(0.2)
    
    # Drag smoothly to the target coordinate
    pyautogui.dragTo(end_x, end_y, duration=1.0, button='left')
    time.sleep(0.2)
    
    # Release mouse button to finish text selection
    pyautogui.mouseUp(button='left')
    time.sleep(ACTION_DELAY)
    
    # Copy selected text
    press_cmd_key('c')
    time.sleep(ACTION_DELAY)
    
    return pyperclip.paste()


def take_screenshot(filename: str):
    """Captures and saves a screenshot with error handling."""
    print(f"--> Capturing screenshot: {filename}...")
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        print(f"✓ Screenshot saved successfully to: {filename}")
    except Exception as e:
        print(f"⚠️ Warning: Screenshot capture failed ({e}).")
        print("   Note: macOS requires Screen Recording permission under System Settings -> Privacy & Security -> Screen Recording.")


# ==============================================================================
# MAIN BOT WORKFLOW
# ==============================================================================
def main():
    print("==================================================")
    print("       🚀 Daily Report Bot Started")
    print("==================================================")
    
    # 1. Date and Filename Calculations
    now = datetime.datetime.now()
    today_date = now.strftime("%Y-%m-%d")
    datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")

    numbers_filename = f"daily_report_{datetime_str}"
    screenshot_filename = f"daily_report_{datetime_str}_screenshot.png"

    time.sleep(1)

    # 2. Launch Chrome & Fetch Webpage Content
    open_app_via_spotlight(CHROME_APP_NAME, wait_seconds=APP_LAUNCH_DELAY)
    navigate_in_browser(TARGET_URL)
    fetched_content = copy_webpage_content()

    # 3. Prepare Structured 3-Column Spreadsheet Row
    snippet = " ".join(fetched_content.split())[:150] if fetched_content else "Sample Documentation"
    row_data = f"{datetime_str}\t{snippet}\t{DEFAULT_COMMENT}"

    # 4. Open Numbers App and Create New Document
    open_app_via_spotlight(NUMBERS_APP_NAME, wait_seconds=APP_LAUNCH_DELAY)
    
    print("--> Creating new spreadsheet document...")
    press_cmd_key('n')
    time.sleep(1.5)
    pyautogui.press('enter')  # Select blank template
    time.sleep(2.0)

    # 5. Paste 3-Column Row into Spreadsheet
    print("--> Pasting 3-column summary row (Date/Time, Snippet, Comment)...")
    pyperclip.copy(row_data)
    press_cmd_key('v')  # Tab-separated paste populates adjacent columns
    time.sleep(1.0)

    # 6. Move to Row Below and Paste Full Content
    print("--> Moving down to next row and pasting sample doc...")
    pyautogui.press('enter')
    time.sleep(ACTION_DELAY)

    full_text_to_paste = f"FastAPI Webpage Contents:\n{fetched_content}"
    pyperclip.copy(full_text_to_paste)
    press_cmd_key('v')
    time.sleep(1.5)

    # 7. Save Numbers Document
    print(f"--> Saving Numbers document as '{numbers_filename}'...")
    press_cmd_key('s')
    time.sleep(1.5)
    pyperclip.copy(numbers_filename)
    press_cmd_key('v')
    time.sleep(ACTION_DELAY)
    pyautogui.press('enter')
    time.sleep(1.5)

    # 8. Take Screenshot
    take_screenshot(screenshot_filename)

    print("==================================================")
    print("       🎉 Daily Report Bot Completed Successfully!")
    print("==================================================")



main()