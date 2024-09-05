import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from fpdf import FPDF
import time
from PIL import Image 
from io import BytesIO

import tkinter as tk
from tkinter import messagebox

def get_report_folder():
    base_path = os.path.dirname(os.path.abspath(__file__))
    report_folder = os.path.join(base_path, "Whatsapp Report")
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)
    return report_folder

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'WhatsApp Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def capture_chat_messages(driver, chat_name, message_dir):
    def safe_text(text):
        # Convert the text to a format that FPDF can handle by ignoring characters not in 'latin-1'
        return text.encode('latin-1', 'ignore').decode('latin-1')

    try:
        print(f"Attempting to capture messages for chat: {chat_name}")

        # Enter the chat
        chat = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[@title='{chat_name}']"))
        )
        chat.click()
        print("Clicked on chat")
        time.sleep(5)  # Wait longer for messages to load

        # Scroll up using JavaScript
        scroll_script = """
        var chatHistory = document.querySelector('div[data-tab="7"]');
        if (chatHistory) {
            chatHistory.scrollTop = 0;
            return true;
        }
        return false;
        """
        scrolled = driver.execute_script(scroll_script)
        print(f"Scroll attempted: {'Success' if scrolled else 'Failed'}")
        time.sleep(3)  # Wait for scrolling to complete

        # Capture messages with sender information
        message_selector = "//div[contains(@class, 'message-in') or contains(@class, 'message-out')]"
        messages = driver.find_elements(By.XPATH, message_selector)

        chat_content = []
        for msg in messages:
            sender = "You" if "message-out" in msg.get_attribute("class") else chat_name
            text = msg.text.strip()
            if text:
                chat_content.append(f"{safe_text(sender)}: {safe_text(text)}")

        print(f"Number of messages captured: {len(chat_content)}")

        # Ensure the base directory exists
        os.makedirs(message_dir, exist_ok=True)

        # Save to file
        file_name = f"{chat_name.replace('/', '_').replace(':', '_')}_messages.txt"
        file_path = os.path.join(message_dir, file_name)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(chat_content))

        print(f"Messages saved for chat: {chat_name}")
        return file_path

    except Exception as e:
        print(f"Error capturing messages for chat {chat_name}: {e}")
        return None

def capture_chats(driver, screenshot_dir, message_dir, max_screenshots=3):
    chat_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "._ajv6.x1y1aw1k.x1sxyh0.xwib8y2.xurb0ha[aria-label='Chats']"))
    )
    chat_button.click()
    time.sleep(2)

    chat_screenshots = []
    message_files = []
    chats = driver.find_elements(By.CSS_SELECTOR, "div[aria-label='Chat list'] > div")
    chats = sorted(chats, key=lambda chat: chat.location['y'])

    for i in range(min(max_screenshots, len(chats))):
        try:
            chat = chats[i]
            driver.execute_script("arguments[0].scrollIntoView();", chat)
            contact_name = chat.find_element(By.CSS_SELECTOR, "span[title]").get_attribute("title")

            # Capture messages
            message_file = capture_chat_messages(driver, contact_name, message_dir)
            if message_file:
                message_files.append((message_file, f"Messages from {contact_name}"))

            # Take screenshot
            screenshot = driver.get_screenshot_as_png()
            image = Image.open(BytesIO(screenshot))
            cropped_image = image.crop((480, 0, 1300, 580)) #left,top,right,bottom
            screenshot_filename = os.path.join(screenshot_dir, f"chat_{i+1}_{contact_name}.png")
            cropped_image.save(screenshot_filename)
            chat_screenshots.append((screenshot_filename, f"Chat {i+1}: {contact_name}"))
            print(f"Chat screenshot saved: {screenshot_filename}")

            # Go back to chat list
            back_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "span[data-testid='back']"))
            )
            back_button.click()
            time.sleep(1)

        except Exception as e:
            print(f"Error processing chat {i+1}: {e}")

    return chat_screenshots, message_files

def capture_profile(driver, screenshot_dir):
    try:
        profile_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "._ajv6.x1y1aw1k.x1sxyh0.xwib8y2.xurb0ha[aria-label='Profile']"))
        )
        profile_button.click()
        time.sleep(2)

        screenshot = driver.get_screenshot_as_png()
        image = Image.open(BytesIO(screenshot))
        cropped_image = image.crop((0, 0, 500, 600)) #left,top,right,bottom
        screenshot_filename = os.path.join(screenshot_dir, "user_profile.png")
        cropped_image.save(screenshot_filename)
        print(f"Profile screenshot saved: {screenshot_filename}")

        return screenshot_filename
    except Exception as e:
        print(f"Error capturing profile: {e}")
        return None

def capture_privacy_settings(driver, screenshot_dir):
    try:
        settings_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "._ajv6.x1y1aw1k.x1sxyh0.xwib8y2.xurb0ha[aria-label='Settings']"))
        )
        settings_button.click()
        time.sleep(1)

        privacy_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Privacy']"))
        )
        privacy_button.click()
        time.sleep(2)

        screenshot = driver.get_screenshot_as_png()
        image = Image.open(BytesIO(screenshot))
        cropped_image = image.crop((0, 0, 500, 600)) #left,top,right,bottom
        screenshot_filename = os.path.join(screenshot_dir, "privacy_settings.png")
        cropped_image.save(screenshot_filename)
        print(f"Privacy settings screenshot saved: {screenshot_filename}")

        return screenshot_filename
    except Exception as e:
        print(f"Error capturing privacy settings: {e}")
        return None

def create_pdf(screenshots, message_files, pdf_file):


    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()
    for screenshot, title in screenshots:
        if screenshot and os.path.exists(screenshot):
            if pdf.get_y() + 100 > pdf.h - 20:
                pdf.add_page()
            pdf.set_font("Arial", 'B', size=12)
            pdf.cell(0, 10, txt=title, ln=True, align='L')
            pdf.image(screenshot, x=10, w=190)
            pdf.ln(10)

    for message_file, title in message_files:
        if message_file and os.path.exists(message_file):
            pdf.add_page()
            pdf.set_font("Arial", 'B', size=12)
            pdf.cell(0, 10, txt=title, ln=True, align='L')
            pdf.set_font("Arial", '', size=10)
            with open(message_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if content:
                    pdf.multi_cell(0, 10, txt=content)
                else:
                    pdf.cell(0, 10, txt="No messages captured for this chat.", ln=True)

    pdf.output(pdf_file)
    print(f"PDF created successfully: {pdf_file}")

def main():
    driver = setup_driver()
    base_dir = "WhatsApp Report"
    screenshot_dir = os.path.join(base_dir, "screenshots")
    message_files_dir = os.path.join(base_dir, "message_files")
    os.makedirs(screenshot_dir, exist_ok=True)
    os.makedirs(message_files_dir, exist_ok=True)

    try:
        driver.get("https://web.whatsapp.com/")
        print("Please scan the QR code.")

        chat_list = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Chat list']"))
        )
        print("QR code scanned successfully. Starting to capture screenshots and messages.")

        time.sleep(3)

        # Capture profile screenshot
        profile_screenshot = capture_profile(driver, screenshot_dir)

        # Capture privacy settings screenshot
        privacy_screenshot = capture_privacy_settings(driver, screenshot_dir)

        # Capture chat screenshots and messages
        chat_screenshots, message_files = capture_chats(driver, screenshot_dir, message_files_dir)

        # Prepare all screenshots for PDF
        all_screenshots = [
            (profile_screenshot, "User Profile"),
            (privacy_screenshot, "Privacy Settings")
        ] + chat_screenshots

        # Create PDF
        pdf_file = os.path.join(base_dir, "whatsapp_report.pdf")
        create_pdf(all_screenshots, message_files, pdf_file)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()
    
    # Show success message and open the report folder
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("Success", "Whatsapp data extraction completed successfully!")
    os.startfile(get_report_folder())

if __name__ == "__main__":
    main()