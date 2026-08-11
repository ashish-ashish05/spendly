import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_PATH = "spendly.db"

def get_db():
    """
    Returns a connection to the SQLite database.
    Enables foreign key support and sets the row factory to sqlite3.Row.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database schema by creating the users and expenses tables.
    """
    conn = get_db()
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    category TEXT NOT NULL,
                    date TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                );
            """)
        print("Database schema initialized successfully.")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def seed_db():
    """
    Populates the database with sample users and expenses for testing purposes.
    Prevents duplicate seeding by checking if users already exist.
    """
    conn = get_db()
    try:
        with conn:
            # Check if users table already contains data
            cursor = conn.execute("SELECT 1 FROM users LIMIT 1")
            if cursor.fetchone():
                print("Database already seeded. Skipping.")
                return

            # Seed Demo User
            demo_user = ("Demo User", "demo@spendly.com", generate_password_hash("demo123"))
            cursor = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                demo_user
            )
            user_id = cursor.lastrowid

            # Seed 8 Sample Expenses covering all categories
            # Categories: Food, Transport, Bills, Health, Entertainment, Shopping, Other
            expenses = [
                (user_id, 12.50, "Food", "2026-08-01", "Lunch at cafe"),
                (user_id, 45.00, "Transport", "2026-08-02", "Weekly fuel"),
                (user_id, 120.00, "Bills", "2026-08-03", "Internet bill"),
                (user_id, 30.00, "Health", "2026-08-04", "Pharmacy"),
                (user_id, 15.00, "Entertainment", "2026-08-05", "Movie ticket"),
                (user_id, 60.00, "Shopping", "2026-08-06", "New t-shirt"),
                (user_id, 10.00, "Other", "2026-08-07", "Parking fee"),
                (user_id, 25.00, "Food", "2026-08-08", "Dinner"),
            ]
            conn.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                expenses
            )

        print("Database seeded successfully with demo data.")
    except sqlite3.Error as e:
        print(f"Error seeding database: {e}")
    finally:
        conn.close()

def create_user(name, email, password_hash):
    """
    Creates a new user in the database.
    Returns the new user's ID on success, or None if the email is already registered.
    """
    conn = get_db()
    try:
        with conn:
            cursor = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, password_hash)
            )
            return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def verify_user(email, password):
    """
    Verifies a user's email and password.
    Returns the user record on success, or None if authentication fails.
    """
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if user and check_password_hash(user['password_hash'], password):
            return user
        return None
    finally:
        conn.close()
