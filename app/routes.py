from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from app import models
from datetime import date
from datetime import datetime
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

    # Convert string dates to datetime objects
    for tx in transactions:
        if isinstance(tx.get('transaction_date'), str):
            tx['transaction_date'] = datetime.strptime(tx['transaction_date'], "%Y-%m-%d")
        if tx.get('created_at') and isinstance(tx['created_at'], str):
            # Assuming created_at is ISO format like '2025-07-24 02:07:17'
            tx['created_at'] = datetime.strptime(tx['created_at'], "%Y-%m-%d %H:%M:%S")

    expense_totals_by_category = models.get_expense_totals_by_category(user_id)
    expense_totals_json = json.dumps(expense_totals_by_category, default=float)

    current_date = date.today().isoformat()

    return render_template(
        'dashboard.html',
        total_income=total_income,
        total_expenses=total_expenses,
        remaining_balance=remaining_balance,
        transactions=transactions,
        income_categories=models.get_all_income_categories(),
        expense_categories=models.get_all_expense_categories(),
        expense_totals_json=expense_totals_json,
        current_date=current_date
    )


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
    

@main.route('/api/current-monthly-budgets', methods=['GET'])
def monthly_budgets():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    try:
        user_id = session['user_id']
        data = models.get_current_monthly_budget_by_category(user_id)
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


@main.route('/dashboard/income')
def income():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = session['user_id']

    # Fetch all income transactions for this user
    income_transactions = models.get_all_income_transactions(user_id)

    # Fetch all income categories for this user
    income_categories = models.get_all_income_categories()

    return render_template('income.html', 
                           incomes=income_transactions, 
                           categories=income_categories)

@main.route('/dashboard/budgets')
def budgets():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = session['user_id']

    # ✅ Fetch all monthly budget data
    all_monthly_budgets = models.get_all_monthly_budgets_by_category(user_id)

    # ✅ Sort by year and month (latest first)
    all_monthly_budgets.sort(key=lambda b: (b['year'], b['month']), reverse=False)

    return render_template(
        'budget.html',
        budgets_by_month=all_monthly_budgets,
        expense_categories=models.get_all_expense_categories(),
    )





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


@main.route('/income/update', methods=['POST'])
def update_income():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    income_id = request.form.get('id')
    category_id = request.form.get('category_id')
    amount = request.form.get('amount')
    description = request.form.get('description')
    transaction_date = request.form.get('transaction_date')

    # Use the model function for updating
    models.update_income_transaction(income_id, session['user_id'], category_id, amount, description, transaction_date)

    flash("Income transaction updated successfully!", "success")
    return redirect(url_for('main.income'))


@main.route('/budgets/add', methods=['POST'])
def add_budget():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    user_id = session['user_id']
    category_id = request.form['category_id']
    budget_amount = request.form['budget_amount']
    month_year = request.form['month_year']  # format: YYYY-MM

    # Extract month and year
    year, month = map(int, month_year.split('-'))

    try:
        models.add_budget_entry(user_id, category_id, budget_amount, month, year)
        flash('Budget added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding budget: {e}', 'danger')

    return redirect(url_for('main.budgets'))


@main.route('/budgets/update', methods=['POST'])
def update_budget():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    budget_id = int(request.form['id'])
    category_id = int(request.form['category_id'])
    budget_amount = float(request.form['budget_amount'])
    consumed = float(request.form['consumed'])
    month_year = request.form['month_year']
    year, month = map(int, month_year.split('-'))

    try:
        models.update_budget_entry(budget_id, category_id, budget_amount, consumed, month, year)
        flash('Budget updated successfully!', 'success')
    except Exception as e:
        flash(str(e), 'danger')  # ✅ Show validation error in flash message

    return redirect(url_for('main.budgets'))



@main.route('/budgets/delete', methods=['POST'])
def delete_budget():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))

    budget_id = int(request.form['id'])

    try:
        models.delete_budget_entry(budget_id)
        flash('Budget deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error deleting budget: {e}', 'danger')

    return redirect(url_for('main.budgets'))














@main.route('/logout')
def logout():
    session.clear()  # Clear session data
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.login'))








