import sqlite3
from typing import Optional, Any, Dict

database_file = "users.db"

def get_db_connection():
    conn = sqlite3.connect(database_file)
    conn.row_factory = sqlite3.Row
    return conn

def create_users_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute()
    conn.commit()
    conn.close()

def add_user(username: str, password: str) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False
    
def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, password FROM users WHERE username = ?",
        (username),
    )

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None

def user_exists(username: str) -> bool:
    return get_user_by_username(username) is not None