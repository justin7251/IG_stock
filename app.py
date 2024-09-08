from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Dummy data for example, but you'd use real stock API in practice
stock_data = {
    "AAPL": {"name": "Apple Inc.", "price": 150.00},
    "GOOGL": {"name": "Alphabet Inc.", "price": 2800.00},
    "AMZN": {"name": "Amazon.com Inc.", "price": 3400.00}
}

# Endpoint 1: /market?searchTerm=stock_name_or_epic
@app.route('/market', methods=['GET'])
def search_market():
    search_term = request.args.get('searchTerm').upper()
    for epic, data in stock_data.items():
        if search_term == epic or search_term in data['name'].upper():
            return jsonify({epic: data})
    return jsonify({"error": "Stock not found"}), 404

# Endpoint 2: /markets?epic=<epic_code>
@app.route('/markets', methods=['GET'])
def get_stock_by_epic():
    epic_code = request.args.get('epic').upper()
    if epic_code in stock_data:
        return jsonify({epic_code: stock_data[epic_code]})
    return jsonify({"error": "Epic code not found"}), 404

if __name__ == '__main__':
    app.run(port=5000)
