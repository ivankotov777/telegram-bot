import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            referred_by INTEGER DEFAULT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER,
            referred_id INTEGER UNIQUE
        )
    """)
    conn.commit()
    conn.close()

def register_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()

def update_user_info(user):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET username = ?, first_name = ?
        WHERE user_id = ?
    """, (user.username, user.first_name, user.id))
    conn.commit()
    conn.close()

def add_referral(referrer_id, referred_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Проверяем: был ли уже зарегистрирован приглашённый
    cursor.execute("SELECT referred_by FROM users WHERE user_id = ?", (referred_id,))
    row = cursor.fetchone()
    if row and row[0] is not None:
        conn.close()
        return  # уже учтён ранее

    # Установить referrer в users
    cursor.execute("UPDATE users SET referred_by = ? WHERE user_id = ?", (referrer_id, referred_id))

    # Добавить в таблицу referrals
    cursor.execute("""
        INSERT OR IGNORE INTO referrals (referrer_id, referred_id)
        VALUES (?, ?)
    """, (referrer_id, referred_id))

    conn.commit()
    conn.close()

def get_referral_count(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ?", (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_by_id(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def reset_referrals():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM referrals")
    cursor.execute("UPDATE users SET referred_by = NULL")
    conn.commit()
    conn.close()