from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import webbrowser
import threading
import signal
from datetime import datetime

app = Flask(__name__)

# Define Excel file paths
DOWNLOADS_FOLDER = os.path.expanduser("~/Downloads")
YEAR = datetime.now().year

EXPENSE_FILE_PATH = os.path.join(DOWNLOADS_FOLDER, f"expense-{YEAR}.xlsx")
FUNDING_FILE_PATH = os.path.join(DOWNLOADS_FOLDER, f"funding-{YEAR}.xlsx")

# Expense types
EXPENSE_TYPES = [
    "General Expense", "OPD Camp Expenses", "Patient Traveling (Non-OPD Camp)",
    "Food & Refreshments", "Office Rent & Utilities", "Transport & Fuel",
    "Purchasing & Maintenance", "Medical Expenses", "Salaries & Staff Welfare"
]

# Funding types
FUNDING_TYPES = [
    "Foreign Funding", "Awareness Funding", "Nutrition Funding",
    "Scholarship", "Sponsorship", "Local Funding"
]

# Payment methods
PAYMENT_METHODS = ["Cashbook", "Cheque"]

# Route to add expenses
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        expense_type = request.form.get('expense_type')
        payment_method = request.form.get('payment_method')
        detail = request.form.get('detail')
        amount = float(request.form.get('amount', 0))
        current_date = datetime.now().strftime("%Y-%m-%d")

        new_data = pd.DataFrame([[current_date, expense_type, payment_method, detail, amount]],
                                columns=["Date", "Expense Type", "Payment Method", "Details", "Amount"])

        if os.path.exists(EXPENSE_FILE_PATH):
            existing_data = pd.read_excel(EXPENSE_FILE_PATH)
            df = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            df = new_data

        df.to_excel(EXPENSE_FILE_PATH, index=False)

    return render_template('index.html', expense_types=EXPENSE_TYPES, payment_methods=PAYMENT_METHODS)

# Route to search expenses
@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    message = ""
    total_expense = 0

    if not os.path.exists(EXPENSE_FILE_PATH):
        message = "No expense records found."
        return render_template('search.html', results=results, message=message, total_expense=total_expense, 
                               expense_types=EXPENSE_TYPES, payment_methods=PAYMENT_METHODS)

    df = pd.read_excel(EXPENSE_FILE_PATH)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    if request.method == 'POST':
        search_date = request.form.get('search_date')
        search_expense = request.form.get('search_expense', "").strip()
        search_payment_method = request.form.get('search_payment_method', "").strip()

        if search_date:
            search_date = pd.to_datetime(search_date).date()
            df = df[df["Date"] == search_date]

        if search_expense and search_expense != "All":
            df = df[df["Expense Type"].str.strip() == search_expense]

        if search_payment_method and search_payment_method != "All":
            df = df[df["Payment Method"].str.strip() == search_payment_method]

        results = df.to_dict(orient="records")
        total_expense = df["Amount"].sum() if not df.empty else 0

    return render_template('search.html', results=results, message=message, total_expense=total_expense, 
                           expense_types=EXPENSE_TYPES, payment_methods=PAYMENT_METHODS)

# Route to add funding
@app.route('/add_funding', methods=['GET', 'POST'])
def add_funding():
    if request.method == 'POST':
        funding_type = request.form.get('funding_type')
        payment_method = request.form.get('payment_method')
        detail = request.form.get('detail')
        amount = float(request.form.get('amount', 0))
        current_date = datetime.now().strftime("%Y-%m-%d")

        new_data = pd.DataFrame([[current_date, funding_type, payment_method, detail, amount]],
                                columns=["Date", "Funding Type", "Payment Method", "Details", "Amount"])

        if os.path.exists(FUNDING_FILE_PATH):
            existing_data = pd.read_excel(FUNDING_FILE_PATH)
            df = pd.concat([existing_data, new_data], ignore_index=True)
        else:
            df = new_data

        df.to_excel(FUNDING_FILE_PATH, index=False)

    return render_template('add_funding.html', funding_types=FUNDING_TYPES, payment_methods=PAYMENT_METHODS)

# Route to search funding
@app.route('/search_funding', methods=['GET', 'POST'])
def search_funding():
    results = []
    message = ""
    total_funding = 0

    if not os.path.exists(FUNDING_FILE_PATH):
        message = "No funding records found."
        return render_template('search_funding.html', results=results, message=message, total_funding=total_funding, 
                               funding_types=FUNDING_TYPES, payment_methods=PAYMENT_METHODS)

    df = pd.read_excel(FUNDING_FILE_PATH)
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    if request.method == 'POST':
        search_date = request.form.get('search_date')
        search_funding_type = request.form.get('search_funding_type', "").strip()
        search_payment_method = request.form.get('search_payment_method', "").strip()

        if search_date:
            search_date = pd.to_datetime(search_date).date()
            df = df[df["Date"] == search_date]

        if search_funding_type and search_funding_type != "All":
            df = df[df["Funding Type"].str.strip() == search_funding_type]

        if search_payment_method and search_payment_method != "All":
            df = df[df["Payment Method"].str.strip() == search_payment_method]

        results = df.to_dict(orient="records")
        total_funding = df["Amount"].sum() if not df.empty else 0

    return render_template('search_funding.html', results=results, message=message, total_funding=total_funding, 
                           funding_types=FUNDING_TYPES, payment_methods=PAYMENT_METHODS)

@app.route('/shutdown', methods=['POST'])
def shutdown():
    response = jsonify({"message": "✅ Server is shutting down successfully!"})
    threading.Timer(1.5, lambda: os.kill(os.getpid(), signal.SIGTERM)).start()
    return response

def run_server():
    app.run(debug=True, use_reloader=False)

if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()
    webbrowser.open("http://127.0.0.1:5000")
