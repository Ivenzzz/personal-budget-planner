from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from app import models

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

    return render_template('dashboard.html',
                           total_income=total_income,
                           total_expenses=total_expenses,
                           remaining_balance=remaining_balance,
                           transactions=transactions)




