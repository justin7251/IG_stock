# IG_stock

1. Create a Virtual Environment

#On macOS/Linux:

```bat
python3 -m venv venv
```

#On Windows:

```bat
python -m venv venv
```

2. Activate the Virtual Environment

#On macOS/Linux:

```bat
source venv/bin/activate
```

#On Windows:

```bat
venv\Scripts\activate
```


3. Package install
pip install -r requirements.txt

4. Access the Endpoints:
To search for a stock: http://127.0.0.1:5000/search_market?searchTerm=AAPL
To get a stock price by EPIC code: http://127.0.0.1:5000/stock_price/AAPL

