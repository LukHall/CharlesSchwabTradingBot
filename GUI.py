import tkinter as tk
import arrow
import requests
import pandas as pd
import numpy as np
import json

from AuthV1 import config, pw, checkAccessToken, cs_login_auth, generate_tokens

# Initialize the timezone
pst_time = arrow.now('US/Pacific')

def update_countdown():
    now = arrow.now('US/Pacific')

    if 'accessT_exp' in config:
        access_time_left = config['accessT_exp'] - now

        access_seconds_left = int(access_time_left.total_seconds())
        if access_seconds_left < 0:
            checkAccessToken(pw['appkey'], pw['secret'], config['refreshT'], config['accessT_exp'],
                             config['redirect_url'])
        # Extract total seconds from timedelta
        access_seconds_left = int(access_time_left.total_seconds())

        # Convert to minutes and seconds for display
        access_minutes, access_seconds = divmod(access_seconds_left, 60)

        # Update the labels
        access_label.config(text=f"Access Token Time Left: {access_minutes:02d}:{access_seconds:02d}")

    root.after(1000, update_countdown)  # Update countdown every second

def generate_tokens_start_timer():
    generate_tokens(pw['appkey'], pw['secret'], config['cs_code'], config['redirect_url'])
    update_countdown()

def fetch_price_history( access_token, symbol='QQQ', period_type='day', period=5, frequency_type='minute', frequency=5,
                        need_extended_hours=False, need_previous_close=False):

    url = f'https://api.schwabapi.com/marketdata/v1/pricehistory'

    params = {
        'symbol': symbol,
        'periodType': period_type,
        'period': period,
        'frequencyType': frequency_type,
        'frequency': frequency,
        'needExtendedHoursData': str(need_extended_hours).lower(),
        'needPreviousClose': str(need_previous_close).lower()
    }

    headers = {
        'accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None


# Create the main window
root = tk.Tk()
root.title("Authentication Interface")
root.geometry("800x600")

# Create and pack the buttons with lambda to delay execution
button1 = tk.Button(root, text="Initialize URL", command=lambda: cs_login_auth(pw['appkey'], config['redirect_url']))
button1.pack(padx=20, pady=10)

button2 = tk.Button(root, text="Generate Tokens", command=lambda: generate_tokens_start_timer())
button2.pack(padx=20, pady=10)

button3 = tk.Button(root, text="Manually Refresh Access Token", command=lambda: checkAccessToken(pw['appkey'], pw['secret'], config['refreshT'], config['accessT_exp'], config['redirect_url']))
button3.pack(padx=20, pady=10)

button4 = tk.Button(root, text="QQQ Price Data", command=lambda: fetch_price_history(config['accessT']))
button4.pack(padx=20, pady=10)

# Create and pack the labels
access_label = tk.Label(root, text="Access Refresh In: ")
access_label.pack(padx=20, pady=10)

# Run the application
root.mainloop()
