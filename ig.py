import os
import json
import requests
import schedule
import time
import datetime
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# IG API credentials from environment variables
IG_API_KEY = os.getenv('IG_API_KEY')
IG_USERNAME = os.getenv('IG_USERNAME')
IG_PASSWORD = os.getenv('IG_PASSWORD')

# EmailJS credentials from environment variables
EMAILJS_SERVICE_ID = os.getenv('EMAILJS_SERVICE_ID')
EMAILJS_TEMPLATE_ID = os.getenv('EMAILJS_TEMPLATE_ID')
EMAILJS_USER_ID = os.getenv('EMAILJS_USER_ID')
EMAILJS_PRIVATE_KEY = os.getenv('EMAILJS_PRIVATE_KEY')

# IG API endpoints
BASE_URL = 'https://api.ig.com/gateway/deal'
SESSION_URL = f'{BASE_URL}/session'
MARKETS_ENDPOINT = f'{BASE_URL}/markets/'  # Replace with the stock's EPIC code

# Headers for API requests
headers = {
    'Content-Type': 'application/json',
    'X-IG-API-KEY': IG_API_KEY,
    'Accept': 'application/json; charset=UTF-8'
}

EMAIL_LOG_FILE = "email_log.json"

# Function to authenticate and get session token
def authenticate():
    payload = {
        'identifier': IG_USERNAME,
        'password': IG_PASSWORD
    }
    response = requests.post(SESSION_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        headers['CST'] = response.headers['CST']
        headers['X-SECURITY-TOKEN'] = response.headers['X-SECURITY-TOKEN']        
        print("Authenticated successfully!")
    else:
        print(f"Failed to authenticate: {response.status_code}")
        exit()

# Function to fetch the current stock price from IG API
def get_stock_price(epic):
    url = MARKETS_ENDPOINT + epic
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        market_data = response.json()
        return market_data['snapshot']['bid']  # Assuming the stock price is in 'bid' key
    else:
        print(f"Failed to fetch stock price for {epic}: {response.status_code}")
        return None

# Function to send an alert email via EmailJS
def send_email_via_emailjs(subject, body):
    email_payload = {
        'service_id': EMAILJS_SERVICE_ID,
        'template_id': EMAILJS_TEMPLATE_ID,
        'user_id': EMAILJS_USER_ID,
        'accessToken': EMAILJS_PRIVATE_KEY,
        'template_params': {
            'subject': subject,
            'message': body
        }
    }

    response = requests.post('https://api.emailjs.com/api/v1.0/email/send', json=email_payload)
    
    if response.status_code == 200:
        print("Email sent successfully!")
    else:
        print(f"Failed to send email: {response.status_code}, {response.text}")

# Function to trigger a sell alert email
def alert_email(stock, epic, price_drop, current_price):
    subject = f"Stock Alert: {stock} (EPIC: {epic_code}) Price Drop {price_drop:.2f}%"
    body = (f"The stock {stock} has dropped by {price_drop:.2f}%.\n"
            f"Current Price: {current_price}.\n"
            "Please consider selling your stock.")
    send_email_via_emailjs(subject, body)
    print(f"Email alert sent for {epic}")

# Function to check the price and compare it with the purchase price
def check_price(stock, epic, purchase_price):
    current_price = get_stock_price(epic)
    if current_price:
        print(f"Current price of {epic}: {current_price}")
        price_drop = ((purchase_price - current_price) / purchase_price) * 100
        
        if price_drop >= 10:
            email_log = load_email_log()
            if not email_already_sent_today(email_log, epic):
                print(f"Price of {epic} has dropped by {price_drop:.2f}%! Sending alert email...")
                alert_email(stock, epic, price_drop, current_price)

                if epic not in email_log:
                    email_log[epic] = []
                email_log[epic].append({'date': str(datetime.date.today()), 'time': str(datetime.datetime.now().time()), 'current_price': current_price})
                save_email_log(email_log)
            else:
                print(f"Email alert for {stock} has already been sent today.")
        else:
            print(f"Price drop is {price_drop:.2f}%, no action needed.")
    else:
        print(f"The price of {epic} has increased or remained the same, no action needed.")

# Function to load email log from the JSON file
def load_email_log():
    if os.path.exists(EMAIL_LOG_FILE):
        with open(EMAIL_LOG_FILE, "r") as file:
            return json.load(file)
    return {}

# Function to save email log to the JSON file
def save_email_log(log):
    with open(EMAIL_LOG_FILE, "w") as file:
        json.dump(log, file, indent=4)
    print(f"Save email log")

# Function to check if an email was already sent today for a specific stock
def email_already_sent_today(log, epic):
    today = str(datetime.date.today())
    # Check if epic exists in log and contains a list of date entries
    if epic in log and isinstance(log[epic], list):
        # Check if any entry for today exists in the list
        return any(entry['date'] == today for entry in log[epic] if 'date' in entry)
    return False


# Function to monitor the stock
def monitor_stock(stock, epic, purchase_price):
    schedule.every(1).minutes.do(check_price, stock=stock, epic=epic, purchase_price=purchase_price)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# Main function to load stock data and start monitoring
if __name__ == '__main__':
    # Authenticate first
    authenticate()

    # Load stock data from stock_data.json
    with open('stock_data.json') as json_file:
        stock_data = json.load(json_file)

    # Iterate through the stock data and monitor stocks that haven't been sold
    for stock, data in stock_data.items():
        if not data.get('sold', False):  # Skip stocks that have been sold
            epic_code = data.get('epic_code', '')  # Get the epic code from stock_data.json

            if epic_code:
                purchase_price = data['purchase_price']
                print(f"Monitoring {stock} (EPIC: {epic_code}) with purchase price {purchase_price}")
                monitor_stock(stock, epic_code, purchase_price)
            else:
                print(f"No stock code found for {stock}, skipping...")
