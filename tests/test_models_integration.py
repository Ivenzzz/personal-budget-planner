import os
import json
import tempfile
import pytest
from datetime import datetime
from flask import Flask
from app import models

@pytest.fixture
def app_context():
    """Setup Flask app context with a temp data path."""
    app = Flask(__name__)
    temp_dir = tempfile.TemporaryDirectory()
    app.config['DATA_PATH'] = temp_dir.name
    with app.app_context():
        # Pre-create empty JSON files
        for f in ['users.json', 'transactions.json', 'categories.json', 'budgets.json']:
            with open(os.path.join(temp_dir.name, f), 'w') as fp:
                json.dump([], fp)
        yield app
    temp_dir.cleanup()


@pytest.fixture
def data_path(app_context):
    return app_context.config['DATA_PATH']


# --------------------
# USER MANAGEMENT
# --------------------

def test_register_and_get_user(app_context):
    user = models.register_user_model("alice", "password123")
    assert user["username"] == "alice"

    fetched = models.get_user_by_username("alice")
    assert fetched["username"] == "alice"

def test_register_duplicate_user(app_context):
    models.register_user_model("bob", "secret")
    with pytest.raises(ValueError, match="Username already exists"):
        models.register_user_model("Bob", "newpass")  # case-insensitive

def test_verify_password(app_context):
    user = models.register_user_model("charlie", "pass123")
    assert models.verify_password(user["password"], "pass123") is True
    assert models.verify_password(user["password"], "wrong") is False


# --------------------
# CATEGORY MANAGEMENT
# --------------------

def test_add_and_get_expense_category(app_context):
    models.add_expense_category(1, "Food", "#FF0000", "expense")
    cats = models.get_all_expense_categories()
    assert len(cats) == 1
    assert cats[0]["name"] == "Food"

def test_add_and_get_income_category(app_context):
    models.add_expense_category(1, "Salary", "#00FF00", "income")
    cats = models.get_all_income_categories()
    assert len(cats) == 1
    assert cats[0]["name"] == "Salary"

def test_delete_category(app_context):
    models.add_expense_category(1, "Travel", "#0000FF", "expense")
    cat_id = models.get_all_expense_categories()[0]["id"]
    models.delete_category(cat_id, 1)
    assert len(models.get_all_expense_categories()) == 0


# --------------------
# TRANSACTIONS & BUDGET
# --------------------

def test_add_budget_and_transaction(app_context):
    # Add category and budget
    models.add_expense_category(1, "Food", "#FF0000", "expense")
    cat_id = models.get_all_expense_categories()[0]["id"]
    models.add_budget_entry(1, cat_id, 500, datetime.now().month, datetime.now().year)

    # Add valid expense
    models.add_transaction(1, cat_id, "expense", 200, "Lunch", datetime.now().strftime("%Y-%m-%d"))
    txs = models.get_user_transactions(1)
    assert len(txs) == 1
    assert txs[0]["amount"] == 200

def test_add_transaction_budget_exceeded(app_context):
    models.add_expense_category(1, "Food", "#FF0000", "expense")
    cat_id = models.get_all_expense_categories()[0]["id"]
    models.add_budget_entry(1, cat_id, 100, datetime.now().month, datetime.now().year)

    # Exceed budget
    with pytest.raises(ValueError, match="Insufficient budget"):
        models.add_transaction(1, cat_id, "expense", 200, "Big Meal", datetime.now().strftime("%Y-%m-%d"))

def test_add_transaction_no_budget(app_context):
    models.add_expense_category(1, "Food", "#FF0000", "expense")
    cat_id = models.get_all_expense_categories()[0]["id"]
    with pytest.raises(ValueError, match="No budget set"):
        models.add_transaction(1, cat_id, "expense", 50, "Snack", datetime.now().strftime("%Y-%m-%d"))


# --------------------
# REPORTING & SUMMARIES
# --------------------

def test_get_totals_income_and_expense(app_context):
    # Setup income and expense categories
    models.add_expense_category(1, "Salary", "#00FF00", "income")
    income_cat = models.get_all_income_categories()[0]["id"]

    models.add_expense_category(1, "Food", "#FF0000", "expense")
    expense_cat = models.get_all_expense_categories()[0]["id"]

    # Add income and budgeted expense
    models.add_budget_entry(1, expense_cat, 300, datetime.now().month, datetime.now().year)
    models.add_transaction(1, income_cat, "income", 1000, "Job", datetime.now().strftime("%Y-%m-%d"))
    models.add_transaction(1, expense_cat, "expense", 100, "Groceries", datetime.now().strftime("%Y-%m-%d"))

    assert models.get_total_income(1) == 1000
    assert models.get_total_expenses(1) == 100
    assert models.get_remaining_balance(1) == 900

def test_expense_and_income_totals_by_category(app_context):
    models.add_expense_category(1, "Salary", "#00FF00", "income")
    income_cat = models.get_all_income_categories()[0]["id"]

    models.add_expense_category(1, "Food", "#FF0000", "expense")
    expense_cat = models.get_all_expense_categories()[0]["id"]

    models.add_budget_entry(1, expense_cat, 500, datetime.now().month, datetime.now().year)
    models.add_transaction(1, income_cat, "income", 2000, "Job", datetime.now().strftime("%Y-%m-%d"))
    models.add_transaction(1, expense_cat, "expense", 300, "Dining", datetime.now().strftime("%Y-%m-%d"))

    exp_totals = models.get_expense_totals_by_category(1)
    inc_totals = models.get_income_totals_by_category(1)

    assert exp_totals[0]["total_amount"] == 300
    assert inc_totals[0]["total_amount"] == 2000


# --------------------
# UPDATE & DELETE TRANSACTIONS
# --------------------

def test_update_and_delete_expense(app_context):
    models.add_expense_category(1, "Food", "#FF0000", "expense")
    cat_id = models.get_all_expense_categories()[0]["id"]
    models.add_budget_entry(1, cat_id, 500, datetime.now().month, datetime.now().year)

    # Add and update expense
    models.add_transaction(1, cat_id, "expense", 100, "Lunch", datetime.now().strftime("%Y-%m-%d"))
    tx_id = models.get_user_transactions(1)[0]["id"]
    models.update_expense_transaction(tx_id, 1, cat_id, 150, "Updated Lunch", datetime.now().strftime("%Y-%m-%d"))

    updated_tx = models.get_user_transactions(1)[0]
    assert updated_tx["amount"] == 150

    # Delete expense
    models.delete_expense_transaction(tx_id, 1)
    assert len(models.get_user_transactions(1)) == 0


def test_update_and_delete_income(app_context):
    models.add_expense_category(1, "Salary", "#00FF00", "income")
    cat_id = models.get_all_income_categories()[0]["id"]

    # Add income and update
    models.add_transaction(1, cat_id, "income", 500, "Pay", datetime.now().strftime("%Y-%m-%d"))
    tx_id = models.get_user_transactions(1)[0]["id"]
    models.update_income_transaction(tx_id, 1, cat_id, 700, "Bonus", datetime.now().strftime("%Y-%m-%d"))

    updated_tx = models.get_user_transactions(1)[0]
    assert updated_tx["amount"] == 700

    # Delete income
    models.delete_income_transaction(tx_id, 1)
    assert len(models.get_user_transactions(1)) == 0


# --------------------
# BUDGET MANAGEMENT
# --------------------

def test_update_and_delete_budget(app_context):
    models.add_expense_category(1, "Rent", "#ABCDEF", "expense")
    cat_id = models.get_all_expense_categories()[0]["id"]

    models.add_budget_entry(1, cat_id, 1000, datetime.now().month, datetime.now().year)
    budget = models.get_all_monthly_budgets_by_category(1)[0]["budgets"][0]
    assert budget["budget_amount"] == 1000

    # Update budget
    models.update_budget_entry(budget["id"], cat_id, 1200, 0, budget["month"], budget["year"])
    updated = models.get_all_monthly_budgets_by_category(1)[0]["budgets"][0]
    assert updated["budget_amount"] == 1200

    # Delete budget
    models.delete_budget_entry(budget["id"])
    assert len(models.get_all_monthly_budgets_by_category(1)) == 0
