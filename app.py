import os
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Flask app initialization
app = Flask(__name__)

# IG API credentials from environment variables
IG_API_KEY = os.getenv('IG_API_KEY')
IG_USERNAME = os.getenv('IG_USERNAME')
IG_PASSWORD = os.getenv('IG_PASSWORD')

# IG API endpoints
BASE_URL = 'https://api.ig.com/gateway/deal'
SESSION_URL = f'{BASE_URL}/session'
MARKETS_ENDPOINT = '/markets/{epic}'  # Stock EPIC code placeholder
MARKET_SEARCH_ENDPOINT = '/markets?searchTerm={epic}'

# Headers for IG API requests
headers = {
    'Content-Type': 'application/json',
    'X-IG-API-KEY': IG_API_KEY,
    'Accept': 'application/json; charset=UTF-8'
}

# Function to authenticate with the IG API
def authenticate():
    payload = {
        'identifier': IG_USERNAME,
        'password': IG_PASSWORD
    }
    response = requests.post(SESSION_URL, headers=headers, json=payload)

    if response.status_code == 200:
        # Save session tokens for future requests
        headers['CST'] = response.headers['CST']
        headers['X-SECURITY-TOKEN'] = response.headers['X-SECURITY-TOKEN']
        print("Authenticated successfully!")
    else:
        print(f"Failed to authenticate: {response.status_code}")
        return None

# Route to search for a market by EPIC code
@app.route('/search_market', methods=['GET'])
def search_market():
    # Get the EPIC code from query parameters
    epic = request.args.get('searchTerm', '').upper()

    if not epic:
        return jsonify({"error": "EPIC code is required"}), 400

    url = BASE_URL + MARKET_SEARCH_ENDPOINT.format(epic=epic)
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        market_data = response.json()
        return jsonify(market_data), 200
    else:
        return jsonify({"error": f"Failed to fetch stock EPIC: {response.status_code}"}), 404

# Route to fetch the stock price for a given EPIC code
@app.route('/stock_price/<epic>', methods=['GET'])
def get_stock_price(epic):
    url = BASE_URL + MARKETS_ENDPOINT.format(epic=epic)
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        market_data = response.json()
        current_price = market_data['snapshot']['bid']
        return jsonify({"epic": epic, "current_price": current_price}), 200
    else:
        return jsonify({"error": f"Failed to fetch stock price: {response.status_code}"}), 404

# Function to check if stock price has dropped and alert
def check_price(epic, purchase_price):
    current_price = get_stock_price(epic)
    if current_price:
        price_drop = ((purchase_price - current_price) / purchase_price) * 100
        if price_drop >= 10:
            print(f"Price dropped by {price_drop:.2f}%! Consider selling stock.")
            # You could add email alerts here
        else:
            print(f"Price drop is {price_drop:.2f}%, no action needed.")
    else:
        print("Failed to fetch the current price.")

# Run the Flask app and authenticate before starting
if __name__ == '__main__':
    authenticate()  # Authenticate once before the app starts
    app.run(debug=True, port=5000)
