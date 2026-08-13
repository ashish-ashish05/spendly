import pytest
import sqlite3
import os
from database.db import init_db, seed_db, get_db
from database.queries import (
    get_user_by_id,
    get_summary_stats,
    get_recent_transactions,
    get_category_breakdown
)

# Override DATABASE_PATH for testing
import database.db
database.db.DATABASE_PATH = "test_spendly.db"

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    if os.path.exists(database.db.DATABASE_PATH):
        os.remove(database.db.DATABASE_PATH)
    init_db()
    seed_db()
    yield
    if os.path.exists(database.db.DATABASE_PATH):
        os.remove(database.db.DATABASE_PATH)

def test_get_user_by_id_valid():
    # Seed user id is 1
    user = get_user_by_id(1)
    assert user is not None
    assert user['name'] == "Demo User"
    assert user['email'] == "demo@spendly.com"
    assert " " in user['member_since']  # Format: Month YYYY

def test_get_user_by_id_invalid():
    user = get_user_by_id(999)
    assert user is None

def test_get_summary_stats_valid():
    # Seed user id is 1
    stats = get_summary_stats(1)
    assert stats['total_spent'] == 317.5
    assert stats['transaction_count'] == 8
    assert stats['top_category'] == "Bills"

def test_get_summary_stats_no_expenses():
    # Create a new user with no expenses
    conn = get_db()
    cursor = conn.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                          ("No Expense User", "no-expense@example.com", "hash"))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    stats = get_summary_stats(user_id)
    assert stats['total_spent'] == 0
    assert stats['transaction_count'] == 0
    assert stats['top_category'] == "—"

def test_get_recent_transactions_valid():
    txs = get_recent_transactions(1)
    assert len(txs) == 10 or len(txs) == 8  # Seed data has 8
    assert txs[0]['amount'] is not None
    # Check ordering (date DESC)
    dates = [t['date'] for t in txs]
    assert dates == sorted(dates, reverse=True)

def test_get_recent_transactions_empty():
    txs = get_recent_transactions(999)
    assert txs == []

def test_get_category_breakdown_valid():
    breakdown = get_category_breakdown(1)
    assert len(breakdown) == 7  # Seed data has 7 categories

    # Check that percentages sum to 100
    total_pct = sum(item['percentage'] for item in breakdown)
    assert total_pct == 100

    # Check ordering by amount DESC
    amounts = [item['amount'] for item in breakdown]
    assert amounts == sorted(amounts, reverse=True)

def test_get_category_breakdown_empty():
    breakdown = get_category_breakdown(999)
    assert breakdown == []
