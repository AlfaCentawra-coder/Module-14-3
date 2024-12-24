import sqlite3

def initiate_db(db_name="initiate.db"):
    """Creates the Products table if it doesn't exist."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            price INTEGER NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def initiate_db(db_name="initiate.db"):
    """Creates the Users table if it doesn't exist."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL,
            balance INTEGER NOT NULL DEFAULT 1000
        )
    """)

    conn.commit()
    conn.close()


def get_all_products(db_name="initiate.db"):

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Products")
    products = cursor.fetchall()

    conn.close()
    return products

def add_user(username, email, age, db_name="initiate.db"):
    """Adds a new user to the Users table with a default balance of 1000."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Users (username, email, age, balance)
        VALUES (?, ?, ?, 1000)
    """, (username, email, age))

    conn.commit()
    conn.close()

def is_included(username, db_name="initiate.db"):
    """Checks if a user with the given username exists in the Users table."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM Users WHERE username = ?", (username,))
    user_exists = cursor.fetchone() is not None

    conn.close()
    return user_exists

