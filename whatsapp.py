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

def capture_chats(driver, screenshot_dir, max_screenshots=5):

    chat_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "._ajv6.x1y1aw1k.x1sxyh0.xwib8y2.xurb0ha[aria-label='Chats']"))
        )
    chat_button.click()
    time.sleep(2)

    chat_screenshots = []
    chats = driver.find_elements(By.CSS_SELECTOR, "div[aria-label='Chat list'] > div")
    chats = sorted(chats, key=lambda chat: chat.location['y'])

    for i in range(min(max_screenshots, len(chats))):
        try:
            chat = chats[i]
            driver.execute_script("arguments[0].scrollIntoView();", chat)
            chat.click()
            time.sleep(1)

            contact_name = chat.find_element(By.CSS_SELECTOR, "span[title]").get_attribute("title")
            screenshot_filename = os.path.join(screenshot_dir, f"chat_{i+1}_{contact_name}.png")
            driver.save_screenshot(screenshot_filename)
            chat_screenshots.append((screenshot_filename, f"Chat {i+1}: {contact_name}"))
            print(f"Chat screenshot saved: {screenshot_filename}")

            back_button = WebDriverWait(driver, 1).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "span[data-testid='back']"))
            )
            back_button.click()
            time.sleep(1)

        except Exception as e:
            print(f"Error processing chat {i+1}: {e}")

    return chat_screenshots

def capture_profile(driver, screenshot_dir):
    try:

        profile_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "._ajv6.x1y1aw1k.x1sxyh0.xwib8y2.xurb0ha[aria-label='Profile']"))
        )
        profile_button.click()
        time.sleep(2)

        screenshot_filename = os.path.join(screenshot_dir, "user_profile.png")
        driver.save_screenshot(screenshot_filename)
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

        screenshot_filename = os.path.join(screenshot_dir, "privacy_settings.png")
        driver.save_screenshot(screenshot_filename)
        print(f"Privacy settings screenshot saved: {screenshot_filename}")

        return screenshot_filename
    except Exception as e:
        print(f"Error capturing privacy settings: {e}")
        return None

def create_pdf(screenshots, pdf_file):
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

    pdf.output(pdf_file)
    print(f"PDF created successfully: {pdf_file}")

def main():
    driver = setup_driver()
    base_dir = "Whatsapp Report"
    screenshot_dir = os.path.join(base_dir, "screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)

    try:
        driver.get("https://web.whatsapp.com/")
        print("Please scan the QR code.")

        chat_list = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[aria-label='Chat list']"))
        )
        print("QR code scanned successfully. Starting to capture screenshots.")

        time.sleep(3)

        # Capture profile screenshot
        profile_screenshot = capture_profile(driver, screenshot_dir)

        # Capture privacy settings screenshot
        privacy_screenshot = capture_privacy_settings(driver, screenshot_dir)

        # Capture chat screenshots
        chat_screenshots = capture_chats(driver, screenshot_dir)


        # Prepare all screenshots for PDF
        all_screenshots = [
            (profile_screenshot, "User Profile"),
            (privacy_screenshot, "Privacy Settings")
        ] + chat_screenshots 

        # Create PDF
        pdf_file = os.path.join(base_dir, "whatsapp_report.pdf")
        create_pdf(all_screenshots, pdf_file)

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