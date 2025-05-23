import tkinter as tk
from tkinter import messagebox, font
import threading
import os

# Import the necessary functions from the existing scripts
from insta_scraper import InstagramScraperApp
from google_scraper import main as google_main
# Import the main functions for WhatsApp, Twitter, and Facebook scraping
# Assuming these are defined in their respective scripts
from whatsapp import main as whatsapp_main
from twitter import TwitterScraperApp
from facebook import FacebookScraperApp

class RoundedButton(tk.Canvas):
    def __init__(self, parent, width, height, cornerradius, padding, color, text, command=None):
        tk.Canvas.__init__(self, parent, borderwidth=0, 
            relief="flat", highlightthickness=0, bg=parent["bg"])
        self.command = command

        if cornerradius > 0.5*width:
            print("Error: cornerradius is greater than width.")
            return None

        if cornerradius > 0.5*height:
            print("Error: cornerradius is greater than height.")
            return None

        rad = 2*cornerradius
        def shape():
            self.create_polygon((padding,height-cornerradius-padding,padding,cornerradius+padding,padding+cornerradius,padding,width-padding-cornerradius,padding,width-padding,cornerradius+padding,width-padding,height-cornerradius-padding,width-padding-cornerradius,height-padding,padding+cornerradius,height-padding), fill=color, outline=color)
            self.create_arc((padding,padding+rad,padding+rad,padding), start=90, extent=90, fill=color, outline=color)
            self.create_arc((width-padding-rad,padding,width-padding,padding+rad), start=0, extent=90, fill=color, outline=color)
            self.create_arc((width-padding,height-rad-padding,width-padding-rad,height-padding), start=270, extent=90, fill=color, outline=color)
            self.create_arc((padding,height-padding-rad,padding+rad,height-padding), start=180, extent=90, fill=color, outline=color)

        id = shape()
        (x0,y0,x1,y1)  = self.bbox("all")
        width = (x1-x0)
        height = (y1-y0)
        self.configure(width=width, height=height)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

        self.textid = self.create_text(width/2, height/2, text=text, fill='white', font=('Helvetica', '10', 'bold'))

    def _on_press(self, event):
        self.configure(relief="sunken")

    def _on_release(self, event):
        self.configure(relief="raised")
        if self.command is not None:
            self.command()

class MainApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Social Media Forensic Tool")
        self.geometry("600x500")
        self.configure(bg='#f0f0f0')

        self.custom_font = font.Font(family="Helvetica", size=12)
        self.header_font = font.Font(family="Helvetica", size=16, weight="bold")

        self.create_widgets()

    def create_widgets(self):
        # Logo (simple text-based logo for this example)
        logo_frame = tk.Frame(self, bg='#3498db', padx=10, pady=10)
        logo_frame.pack(fill=tk.X)
        logo = tk.Label(logo_frame, text="🔍", font=("Helvetica", 24), bg='#3498db', fg='white')
        logo.pack()

        # Header
        header = tk.Label(self, text="Social Media Forensic Tool", font=self.header_font, bg='#f0f0f0', fg='#2c3e50')
        header.pack(pady=20)

        # Subheader
        subheader = tk.Label(self, text="What data would you like to extract?", font=self.custom_font, bg='#f0f0f0', fg='#34495e')
        subheader.pack(pady=10)

        # Button frame
        button_frame = tk.Frame(self, bg='#f0f0f0')
        button_frame.pack(pady=20)

        # Instagram button
        self.instagram_button = RoundedButton(button_frame, 150, 40, 10, 2, '#f56040', "Instagram", self.start_instagram)
        self.instagram_button.grid(row=0, column=0, padx=20, pady=20)

        # Google button
        self.google_button = RoundedButton(button_frame, 150, 40, 10, 2, '#34a853', "Google", self.start_google)
        self.google_button.grid(row=0, column=1, padx=20, pady=20)

        # WhatsApp button
        self.whatsapp_button = RoundedButton(button_frame, 150, 40, 10, 2, '#075e54', "WhatsApp", self.start_whatsapp)
        self.whatsapp_button.grid(row=0, column=2, padx=20, pady=20)

        # Twitter button
        self.twitter_button = RoundedButton(button_frame, 150, 40, 10, 2, '#000000', "Twitter", self.start_twitter)
        self.twitter_button.grid(row=1, column=0, padx=20, pady=20)

        # Facebook button
        self.facebook_button = RoundedButton(button_frame, 150, 40, 10, 2, '#3b5998', "Facebook", self.start_facebook)
        self.facebook_button.grid(row=1, column=1, padx=20, pady=20)

        # Telegram button
        self.facebook_button = RoundedButton(button_frame, 150, 40, 10, 2, '#01acee', "Telegram", self.start_facebook)
        self.facebook_button.grid(row=1, column=2, padx=20, pady=20)

        # Quit button
        self.quit_button = RoundedButton(self, 100, 40, 10, 2, '#95a5a6', "Quit", self.quit)
        self.quit_button.pack(side=tk.BOTTOM, pady=20)

    def start_instagram(self):
        self.destroy()  # Close the main window
        instagram_app = InstagramScraperApp()
        instagram_app.mainloop()

    def start_google(self):
        threading.Thread(target=self.run_google_scraper).start()

    def start_whatsapp(self):
        threading.Thread(target=self.run_whatsapp_scraper).start()

    def start_twitter(self):
        self.destroy()  # Close the main window
        twitter_app = TwitterScraperApp()
        twitter_app.mainloop()
    
    def start_facebook(self):
        self.destroy()  # Close the main window
        facebook_app = FacebookScraperApp()
        facebook_app.mainloop()


    def run_google_scraper(self):
        try:
            google_main()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during Google scraping: {str(e)}")

    def run_whatsapp_scraper(self):
        try:
            whatsapp_main()
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during WhatsApp scraping: {str(e)}")

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
