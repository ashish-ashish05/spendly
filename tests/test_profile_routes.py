import pytest
from app import app
from database.db import init_db, seed_db, get_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret'
    with app.test_client() as client:
        with app.app_context():
            # Use a clean test DB
            import database.db
            database.db.DATABASE_PATH = "test_route_spendly.db"
            init_db()
            seed_db()
        yield client

    import os
    if os.path.exists("test_route_spendly.db"):
        os.remove("test_route_spendly.db")

def test_profile_unauthenticated(client):
    response = client.get("/profile", follow_redirects=False)
    assert response.status_code == 302
    assert response.location.endswith("/login")

def test_profile_authenticated_seed_user(client):
    with client.session_transaction() as sess:
        sess['user_id'] = 1

    response = client.get("/profile")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Demo User" in html
    assert "demo@spendly.com" in html
    assert "₹" in html
    assert "Bills" in html

def test_profile_new_user(client):
    # Create a new user
    with app.app_context():
        conn = get_db()
        cursor = conn.execute("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                              ("New User", "new@example.com", "hash"))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()

    with client.session_transaction() as sess:
        sess['user_id'] = user_id

    response = client.get("/profile")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "New User" in html
    assert "₹0" in html # Check for zero spent
