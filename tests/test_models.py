import os
import json
import pytest
import bcrypt
from unittest.mock import patch, mock_open
from flask import Flask
from app import models  # Adjust import if module is named differently

# ---------- FIXTURE FOR FLASK APP CONTEXT ----------
@pytest.fixture
def app_context(tmp_path):
    """Provide a Flask app context with a temp DATA_PATH."""
    app = Flask(__name__)
    app.config['DATA_PATH'] = tmp_path
    with app.app_context():
        yield app

# ---------- JSON UTIL TESTS ----------
def test_save_and_load_json(app_context):
    data = [{"id": 1, "name": "Test"}]
    file = "test.json"

    # Save JSON
    models.save_json(file, data)

    # Verify file exists and reload content
    file_path = os.path.join(app_context.config['DATA_PATH'], file)
    assert os.path.exists(file_path)
    loaded = models.load_json(file)
    assert loaded == data

def test_load_json_creates_empty_file(app_context):
    file = "new.json"
    result = models.load_json(file)
    assert result == []  # Should create an empty file and return []

# ---------- PASSWORD UTILS ----------
def test_password_hash_and_verify():
    password = "securepass"
    hashed = models.hash_password(password)
    assert bcrypt.checkpw(password.encode(), hashed.encode())
    assert models.verify_password(hashed, password)
    assert not models.verify_password(hashed, "wrongpass")

# ---------- USER FUNCTIONS ----------
@patch("app.models.load_json", return_value=[{"username": "alice", "id": 1, "password": "x"}])
def test_get_user_by_username(mock_load):
    user = models.get_user_by_username("alice")
    assert user is not None
    assert user["username"] == "alice"

@patch("app.models.load_json", return_value=[])
@patch("app.models.save_json")
def test_register_user_model(mock_save, mock_load, app_context):
    user = models.register_user_model("bob", "password123")
    assert user["username"] == "bob"
    assert "password" in user
    mock_save.assert_called_once()

@patch("app.models.load_json", return_value=[{"username": "bob", "id": 1, "password": "x"}])
def test_register_user_existing(mock_load, app_context):
    with pytest.raises(ValueError, match="Username already exists"):
        models.register_user_model("bob", "newpass")

# ---------- TRANSACTION FUNCTIONS ----------
@patch("app.models.load_json")
def test_get_user_transactions(mock_load):
    mock_load.return_value = [
        {"id": 1, "user_id": 1, "category_id": 2, "amount": "50", "type": "expense"},
        {"id": 2, "user_id": 2, "category_id": 2, "amount": "20", "type": "income"}
    ]
    txs = models.get_user_transactions(1)
    assert len(txs) == 1
    assert isinstance(txs[0]["amount"], float)
    assert txs[0]["user_id"] == 1

# ---------- BUDGET VALIDATION ----------
@patch("app.models.load_json")
@patch("app.models.save_json")
def test_add_transaction_budget_violation(mock_save, mock_load, app_context):
    mock_load.side_effect = [
        [],  # transactions.json
        [{"user_id": 1, "category_id": 1, "month": 7, "year": 2025, "budget_amount": 100, "consumed": 90}]  # budgets.json
    ]
    with pytest.raises(ValueError, match="Insufficient budget"):
        models.add_transaction(1, 1, "expense", 50, "Test expense", "2025-07-31")

# ---------- CATEGORY FUNCTIONS ----------
@patch("app.models.load_json", return_value=[
    {"id": 1, "name": "Salary", "type": "income"},
    {"id": 2, "name": "Food", "type": "expense"},
])
def test_get_income_and_expense_categories(mock_load):
    incomes = models.get_all_income_categories()
    expenses = models.get_all_expense_categories()
    assert all(c["type"] == "income" for c in incomes)
    assert all(c["type"] == "expense" for c in expenses)
