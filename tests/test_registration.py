import pytest
from app import app
from database.db import get_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def db_conn():
    return get_db()

def test_register_success(client, db_conn):
    # Test successful registration
    email = "testuser@example.com"
    response = client.post("/register", data={
        "name": "Test User",
        "email": email,
        "password": "password123"
    }, follow_redirects=True)

    assert response.status_code == 200
    # Should redirect to login page
    assert b"Sign in" in response.data

    # Verify user exists in DB
    user = db_conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    assert user is not None
    assert user["name"] == "Test User"
    # Verify password is not plain text
    assert user["password_hash"] != "password123"

def test_register_duplicate_email(client):
    # Test registration with duplicate email (demo user exists from seed_db)
    email = "demo@spendly.com"
    response = client.post("/register", data={
        "name": "Another User",
        "email": email,
        "password": "password123"
    })

    assert response.status_code == 200
    assert b"Email already registered" in response.data

def test_register_missing_fields(client):
    # Test registration with missing name
    response = client.post("/register", data={
        "name": "",
        "email": "missing@example.com",
        "password": "password123"
    })

    assert response.status_code == 200
    assert b"All fields are required" in response.data

def test_register_empty_fields(client):
    # Test registration with whitespace only
    response = client.post("/register", data={
        "name": "   ",
        "email": "empty@example.com",
        "password": "password123"
    })

    assert response.status_code == 200
    assert b"All fields are required" in response.data
