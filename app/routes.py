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

    expense_totals_by_category = models.get_expense_totals_by_category(user_id)
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
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        user_id = session['user_id']
        data = models.get_expense_totals_by_category(user_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/income-totals', methods=['GET'])
def income_totals():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        user_id = session['user_id']
        data = models.get_income_totals_by_category(user_id)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@main.route('/api/monthly-expenses', methods=['GET'])
def monthly_expenses():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        user_id = session['user_id']
        data = models.get_monthly_expenses(user_id)  # <-- Correct function
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500




@main.route('/dashboard/expenses')
def expenses():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = session['user_id']

    # Fetch all expense transactions for this user
    expenses_transactions = models.get_all_expense_transactions(user_id)

    # Fetch all expense categories for this user
    expense_categories = models.get_all_expense_categories()

    return render_template('expenses.html', 
                           expenses=expenses_transactions, 
                           categories=expense_categories)


@main.route('/dashboard/expenses/update', methods=['POST'])
def update_expense():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    expense_id = request.form['id']
    date = request.form['transaction_date']
    category_id = request.form['category_id']
    amount = request.form['amount']
    description = request.form['description']

    try:
        models.update_expense_transaction(expense_id, session['user_id'], category_id, amount, description, date)
        flash('Expense updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating expense: {e}', 'danger')

    return redirect(url_for('main.expenses'))

@main.route('/expenses/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    try:
        models.delete_expense_transaction(expense_id, session['user_id'])
        flash('Expense deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting expense: {e}', 'danger')

    return redirect(url_for('main.expenses'))










