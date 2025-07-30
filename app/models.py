import os
import json
import bcrypt
from flask import current_app
from datetime import datetime
import calendar

# -------------------- JSON UTILS --------------------
def load_json(filename):
    file_path = os.path.join(current_app.config['DATA_PATH'], filename)
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            json.dump([], f)
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(filename, data):
    file_path = os.path.join(current_app.config['DATA_PATH'], filename)
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

# -------------------- PASSWORD UTILS --------------------
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

def parse_datetime(dt_str):
    """Parse date strings that may be 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'."""
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.strptime(dt_str, "%Y-%m-%d")


# -------------------- USER FUNCTIONS --------------------
def get_user_by_username(username):
    users = load_json('users.json')
    return next((u for u in users if u['username'] == username), None)

def create_user(username, password, user_type='user'):
    users = load_json('users.json')
    new_user = {
        "id": len(users) + 1,
        "username": username,
        "password": hash_password(password),
        "type": user_type
    }
    users.append(new_user)
    save_json('users.json', users)

# -------------------- TRANSACTION FUNCTIONS --------------------
def get_user_transactions(user_id):
    transactions = load_json('transactions.json')
    return [
        {
            **t,
            "category_id": int(t["category_id"]),  # ✅ normalize
            "user_id": int(t["user_id"]),
            "amount": float(t["amount"])
        }
        for t in transactions if int(t["user_id"]) == int(user_id)
    ]


def add_transaction(user_id, category_id, t_type, amount, description, date):
    transactions = load_json('transactions.json')

    # Combine the provided date with the current time
    current_time = datetime.now().strftime("%H:%M:%S")
    transaction_datetime = f"{date} {current_time}"  # e.g., "2025-07-30 14:35:22"

    new_tx = {
        "id": len(transactions) + 1,
        "user_id": user_id,
        "category_id": category_id,
        "type": t_type,
        "amount": float(amount),
        "description": description,
        "transaction_date": transaction_datetime  # ✅ Date + Time stored here
    }

    transactions.append(new_tx)
    save_json('transactions.json', transactions)

# -------------------- SUMMARY FUNCTIONS --------------------
def get_total_expenses(user_id):
    transactions = get_user_transactions(user_id)
    return sum(t['amount'] for t in transactions if t['type'] == 'expense')

def get_total_income(user_id):
    transactions = get_user_transactions(user_id)
    return sum(t['amount'] for t in transactions if t['type'] == 'income')

def get_remaining_balance(user_id):
    return get_total_income(user_id) - get_total_expenses(user_id)

def get_all_transactions(user_id):
    transactions = get_user_transactions(user_id)
    categories = load_json('categories.json')

    category_map = {int(c['id']): c['name'] for c in categories}

    for t in transactions:
        t['category_name'] = category_map.get(int(t['category_id']), "Unknown")
        
        # ✅ Handle both formats
        if isinstance(t['transaction_date'], str):
            t['transaction_date'] = parse_datetime(t['transaction_date'])

    return sorted(transactions, key=lambda t: t['transaction_date'], reverse=True)[:5]


def get_all_expense_transactions(user_id):
    transactions = load_json('transactions.json')
    categories = load_json('categories.json')

    # Map category IDs to names
    category_map = {int(c['id']): c['name'] for c in categories}

    expenses = []
    for t in transactions:
        if t["type"] == "expense" and int(t["user_id"]) == int(user_id):
            # ✅ Convert transaction_date safely
            tx_date = t["transaction_date"]
            if isinstance(tx_date, str):
                try:
                    tx_date = datetime.strptime(tx_date, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    tx_date = datetime.strptime(tx_date, "%Y-%m-%d")  # fallback for old data

            expenses.append({
                **t,
                "category_id": int(t["category_id"]),
                "user_id": int(t["user_id"]),
                "amount": float(t["amount"]),
                "category_name": category_map.get(int(t["category_id"]), "Unknown"),
                "transaction_date": tx_date,  # ✅ Now it's a datetime object
            })

    return expenses

def get_all_income_transactions(user_id):
    transactions = load_json('transactions.json')
    categories = load_json('categories.json')

    category_map = {int(c['id']): c['name'] for c in categories}

    incomes = []
    for t in transactions:
        if t["type"] == "income" and int(t["user_id"]) == int(user_id):
            incomes.append({
                **t,
                "category_id": int(t["category_id"]),
                "user_id": int(t["user_id"]),
                "amount": float(t["amount"]),
                "category_name": category_map.get(int(t["category_id"]), "Unknown"),
                "transaction_date": datetime.strptime(
                    t["transaction_date"], "%Y-%m-%d %H:%M:%S" if " " in t["transaction_date"] else "%Y-%m-%d"
                )
            })
    return incomes



# -------------------- CATEGORY FUNCTIONS --------------------
def get_all_income_categories():
    categories = load_json('categories.json')
    return [c for c in categories if c['type'] == 'income']

def get_all_expense_categories():
    categories = load_json('categories.json')
    return [c for c in categories if c['type'] == 'expense']

def add_income(user_id, amount, category_id, transaction_date, description):
    add_transaction(user_id, category_id, 'income', amount, description, transaction_date)

# -------------------- REPORT FUNCTIONS --------------------
def get_expense_totals_by_category(user_id):
    transactions = get_all_expense_transactions(user_id)
    categories = load_json('categories.json')
    results = []

    for cat in get_all_expense_categories():
        total = sum(
            t['amount'] 
            for t in transactions 
            if int(t['category_id']) == int(cat['id'])  # ✅ Ensure both are int
        )
        if total > 0:
            results.append({
                "category_name": cat['name'],
                "total_amount": total
            })

    return results


def get_income_totals_by_category(user_id):
    transactions = get_user_transactions(user_id)
    results = []
    
    for cat in get_all_income_categories():
        total = sum(
            t['amount']
            for t in transactions
            if int(t['category_id']) == int(cat['id'])  # ✅ normalize IDs
        )
        if total > 0:
            results.append({
                "category_name": cat['name'],
                "total_amount": total
            })
    
    return results


def get_daily_expenses():
    transactions = load_json('transactions.json')
    expenses = [t for t in transactions if t['type'] == 'expense']
    daily_totals = {}
    for t in expenses:
        daily_totals[t['transaction_date']] = daily_totals.get(t['transaction_date'], 0) + t['amount']
    return [{"transaction_date": d, "total_amount": amt} for d, amt in daily_totals.items()]

# -------------------- UPDATE & DELETE --------------------
def update_expense_transaction(expense_id, user_id, category_id, amount, description, date):
    transactions = load_json('transactions.json')
    expense_id = int(expense_id)
    user_id = int(user_id)

    updated = False
    for t in transactions:
        if int(t['id']) == expense_id and int(t['user_id']) == user_id and t['type'] == 'expense':
            t.update({
                "category_id": int(category_id),
                "amount": float(amount),
                "description": description,
                "transaction_date": date
            })
            updated = True
            break  # ✅ Stop after updating

    if updated:
        save_json('transactions.json', transactions)
    else:
        print(f"⚠️ Expense with ID {expense_id} not found or user mismatch.")


def delete_expense_transaction(expense_id, user_id):
    transactions = load_json('transactions.json')
    transactions = [t for t in transactions if not (t['id'] == expense_id and t['user_id'] == user_id and t['type'] == 'expense')]
    save_json('transactions.json', transactions)


def update_income_transaction(income_id, user_id, category_id, amount, description, date):
    transactions = load_json('transactions.json')
    for t in transactions:
        if t['id'] == int(income_id) and t['user_id'] == int(user_id) and t['type'] == 'income':
            t.update({
                "category_id": int(category_id),
                "amount": float(amount),
                "description": description,
                "transaction_date": date
            })
            break
    save_json('transactions.json', transactions)


def get_current_monthly_budget_by_category(user_id):
    budgets = load_json('budgets.json')
    categories = load_json('categories.json')
    current_month = datetime.now().month
    current_year = datetime.now().year

    results = []
    total_budget = 0.0
    total_consumed = 0.0

    for b in budgets:
        if b['user_id'] == user_id and b['month'] == current_month and b['year'] == current_year:
            category = next((c for c in categories if c['id'] == b['category_id']), None)
            if category:
                budget_amount = b.get('budget_amount', 0.0)
                consumed = b.get('consumed', 0.0)

                results.append({
                    "category_name": category['name'],
                    "budget_amount": budget_amount,
                    "consumed": consumed,
                    "color": category.get('color', "#9CA3AF")  # Default gray if missing
                })

                total_budget += budget_amount
                total_consumed += consumed

    return {
        "month": current_month,
        "month_name": calendar.month_name[current_month],
        "year": current_year,
        "budgets": results,
        "total_budget": total_budget,
        "total_consumed": total_consumed,
        "remaining": total_budget - total_consumed
    }



def get_all_monthly_budgets_by_category(user_id):
    budgets = load_json('budgets.json')
    categories = load_json('categories.json')

    grouped_results = {}

    for b in budgets:
        if b['user_id'] == user_id:
            category = next((c for c in categories if c['id'] == b['category_id']), None)
            if category:
                key = (b['month'], b['year'])
                if key not in grouped_results:
                    grouped_results[key] = {
                        "month": b['month'],
                        "month_name": calendar.month_name[b['month']],
                        "year": b['year'],
                        "budgets": []
                    }

                grouped_results[key]["budgets"].append({
                    "id": b["id"],
                    "category_id": b["category_id"],
                    "category_name": category['name'],
                    "budget_amount": b['budget_amount'],
                    "consumed": b.get('consumed', 0.00),
                    "month": b["month"],           # ✅ Added
                    "year": b["year"],             # ✅ Added
                    "color": category.get('color', "#9CA3AF")
                })

    results = sorted(grouped_results.values(), key=lambda x: (x["year"], x["month"]), reverse=True)
    return results



def add_budget_entry(user_id, category_id, budget_amount, month, year):
    budgets = load_json('budgets.json')

    # Generate a new ID (incremental based on max ID)
    new_id = max([b['id'] for b in budgets], default=0) + 1

    # Create new budget record
    new_budget = {
        "id": new_id,
        "user_id": int(user_id),
        "category_id": int(category_id),
        "budget_amount": float(budget_amount),
        "consumed": 0.0,  # Default consumed amount
        "month": month,
        "year": year,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    budgets.append(new_budget)
    save_json('budgets.json', budgets)


def update_budget_entry(budget_id, category_id, budget_amount, consumed, month, year):
    budgets = load_json('budgets.json')
    budget = next((b for b in budgets if b['id'] == budget_id), None)
    if not budget:
        raise ValueError(f"Budget with ID {budget_id} not found.")

    # ✅ Validation: Budget amount cannot be less than consumed
    if float(budget_amount) < float(budget['consumed']):
        raise ValueError("Budget amount cannot be less than the consumed amount.")

    # Update fields if valid
    budget['category_id'] = int(category_id)
    budget['budget_amount'] = float(budget_amount)
    budget['consumed'] = float(consumed)  # Read-only but persisted
    budget['month'] = int(month)
    budget['year'] = int(year)

    save_json('budgets.json', budgets)



def delete_budget_entry(budget_id):
    budgets = load_json('budgets.json')

    # Check if budget exists
    budget = next((b for b in budgets if b['id'] == budget_id), None)
    if not budget:
        raise ValueError(f"Budget with ID {budget_id} not found.")

    # Remove the budget
    budgets = [b for b in budgets if b['id'] != budget_id]

    save_json('budgets.json', budgets)


def add_expense_category(name, color, category_type):
    categories = load_json('categories.json')

    # Generate a new ID (incremental)
    new_id = max([c['id'] for c in categories], default=0) + 1

    # Create new category record
    new_category = {
        "id": new_id,
        "name": name,
        "color": color,
        "type": category_type  # e.g., "expense"
    }

    categories.append(new_category)
    save_json('categories.json', categories)








