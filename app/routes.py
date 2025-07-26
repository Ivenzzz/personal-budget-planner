from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from app import models
from datetime import date
from flask import jsonify
import json

main = Blueprint('main', __name__, template_folder='../templates')

@main.route('/')
def index():
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = models.get_user_by_username(request.form['username'])
        if user and models.verify_password(user['password'], request.form['password']):
            session['user_id'] = user['id']
            return redirect(url_for('main.dashboard'))
        flash("Invalid credentials")
    return render_template('login.html')


# @main.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         models.create_user(request.form['username'], request.form['password'])
#         return redirect(url_for('main.login'))
#     return render_template('register.html')

@main.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    total_income = models.get_total_income(user_id)
    total_expenses = models.get_total_expenses(user_id)
    remaining_balance = models.get_remaining_balance(user_id)
    transactions = models.get_all_transactions(user_id)

    income_categories = models.get_all_income_categories()
    expense_categories = models.get_all_expense_categories()

    expense_totals_by_category = models.get_expense_totals_by_category()
    expense_totals_json = json.dumps(expense_totals_by_category, default=float)

    current_date = date.today().isoformat()

    return render_template('dashboard.html',
                           total_income=total_income,
                           total_expenses=total_expenses,
                           remaining_balance=remaining_balance,
                           transactions=transactions,
                           income_categories=income_categories,
                           expense_categories=expense_categories, 
                           expense_totals_json=expense_totals_json,
                           current_date=current_date)


@main.route('/add-income', methods=['POST'])
def add_income():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    amount = request.form['amount']
    category_id = request.form['category_id']
    transaction_date = request.form['transaction_date']
    description = request.form.get('description', '')  # <-- Added

    models.add_income(user_id, amount, category_id, transaction_date, description)  # <-- Updated

    flash("Income added successfully!")
    return redirect(url_for('main.dashboard'))


@main.route('/add-expense', methods=['POST'])
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    amount = request.form['amount']
    category_id = request.form['category_id']
    description = request.form.get('description', '')
    transaction_date = request.form['transaction_date']

    models.add_transaction(user_id, category_id, 'expense', amount, description, transaction_date)
    flash("Expense added successfully!")
    return redirect(url_for('main.dashboard'))

@main.route('/api/expense-totals', methods=['GET'])
def expense_totals():
    try:
        data = models.get_expense_totals_by_category()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500







