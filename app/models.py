import mysql.connector
import os
import bcrypt
from flask import current_app

def get_db_connection():
    return mysql.connector.connect(**current_app.config['DB_CONFIG'])

def hash_password(password):
    # bcrypt automatically handles salting internally
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(stored_password, provided_password):
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))


def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, password, type FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def create_user(username, password, user_type='user'):
    hashed_password = hash_password(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, password, type) VALUES (%s, %s, %s)
    """, (username, hashed_password, user_type))
    conn.commit()
    cursor.close()
    conn.close()


def get_user_transactions(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT t.*, c.name as category_name 
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = %s
        ORDER BY t.transaction_date DESC
    """, (user_id,))
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

def add_transaction(user_id, category_id, t_type, amount, description, date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (user_id, category_id, type, amount, description, transaction_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, category_id, t_type, amount, description, date))
    conn.commit()
    cursor.close()
    conn.close()


def get_total_expenses(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE user_id = %s AND type = 'expense'
    """, (user_id,))
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total

def get_total_income(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COALESCE(SUM(amount), 0)
        FROM transactions
        WHERE user_id = %s AND type = 'income'
    """, (user_id,))
    total = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return total

def get_remaining_balance(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) -
            COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0)
        FROM transactions
        WHERE user_id = %s
    """, (user_id,))
    
    balance = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return balance

def get_all_transactions(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            t.id,
            t.type,
            t.amount,
            t.description,
            t.transaction_date,
            c.name AS category_name,
            c.type AS category_type
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = %s
        ORDER BY t.transaction_date DESC, t.created_at DESC
    """, (user_id,))

    transactions = cursor.fetchall()
    cursor.close()
    conn.close()
    return transactions





