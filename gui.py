import tkinter as tk
from tkcalendar import Calendar,DateEntry
import json
import os

# File to store stock data
stock_data_file = 'stock_data.json'

# Save purchase price to JSON
def save_purchase_data(epic_code, purchase_price, purchase_date):
    if os.path.exists(stock_data_file):
        with open(stock_data_file, 'r') as f:
            data = json.load(f)
    else:
        data = {}

    data[epic_code] = {"purchase_price": float(purchase_price), "purchase_date": purchase_date}

    with open(stock_data_file, 'w') as f:
        json.dump(data, f)
    
    result_label.config(text=f'Stored {epic_code} purchase price.')

# GUI setup
def create_gui():
    root = tk.Tk()

    root.geometry("300x300")
    root.title("Stock Purchase Price")

    tk.Label(root, text="Epic Code").pack(pady=10)
    epic_entry = tk.Entry(root).pack(pady=5)
    tk.Label(root, text="Purchase Price").pack(pady=10)
    price_entry = tk.Entry(root).pack(pady=5)

    tk.Label(root, text='Purchase Date').pack(pady=10)



    purchase_date_entry = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2).pack(pady=10)
   
    save_button = tk.Button(root, text='Save', command=lambda: save_purchase_data(epic_entry.get(), price_entry.get(), purchase_date_entry.get()))
    save_button.pack(pady=20)

    global result_label
    result_label = tk.Label(root, text="")
    result_label.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    create_gui()
