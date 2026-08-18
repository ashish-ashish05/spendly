import pytest
from flask import url_for
from app import app as flask_app
from database.db import init_db
import sqlite3


@pytest.fixture
def app():
    flask_app.config.update(
        {
            "TESTING": True,
            "DATABASE": "test_delete_expense.db",
            "SECRET_KEY": "test-secret",
            "WTF_CSRF_ENABLED": False,
        }
    )
    with flask_app.app_context():
        init_db()
        yield flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    # Note: Using the registration/login flow to establish a session
    client.post(
        "/register",
        data={"name": "Test User", "email": "test@example.com", "password": "testpass"},
    )
    client.post("/login", data={"email": "test@example.com", "password": "testpass"})
    return client


def seed_expense(
    app,
    user_id,
    amount=10.0,
    category="Food",
    date="2023-01-01",
    description="Test Expense",
):
    """Helper to insert an expense into the in-memory database."""
    with app.app_context():
        # Use the internal DB connection logic if available,
        # otherwise we use a direct connection to the :memory: DB.
        # Since the app uses a specific way to handle connections (likely in database/db.py),
        # we'll access the DB via the app's configured DATABASE.
        conn = sqlite3.connect(app.config["DATABASE"])
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            (user_id, amount, category, date, description),
        )
        expense_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return expense_id


class TestDeleteExpense:
    def test_delete_unauthenticated_redirects_to_login(self, client):
        """Accessing delete route while logged out should redirect to /login."""
        response = client.get(url_for("delete_expense_route", id=1))
        assert response.status_code == 302
        assert response.location == url_for("login", )

    def test_delete_non_existent_expense_returns_404(self, auth_client):
        """Trying to delete an expense with an invalid ID should return a 404."""
        response = auth_client.get(url_for("delete_expense_route", id=999))
        assert response.status_code == 404

    def test_delete_unauthorized_expense_returns_404(self, app, auth_client, client):
        """Trying to delete an expense that belongs to another user should return a 404."""
        # 1. Create a second user
        client.post(
            "/register",
            data={
                "name": "Other User",
                "email": "other@example.com",
                "password": "otherpass",
            },
        )

        # Get IDs for both users
        with app.app_context():
            conn = sqlite3.connect(app.config["DATABASE"])
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE email = ?", ("test@example.com",)
            )
            user_a_id = cursor.fetchone()[0]
            cursor.execute(
                "SELECT id FROM users WHERE email = ?", ("other@example.com",)
            )
            user_b_id = cursor.fetchone()[0]
            conn.close()

        # 2. Create an expense for User A
        expense_id = seed_expense(app, user_a_id)

        # 3. Log in as User B
        auth_client_b = client
        auth_client_b.post(
            "/login", data={"email": "other@example.com", "password": "otherpass"}
        )

        # 4. User B tries to delete User A's expense
        response = auth_client_b.get(url_for("delete_expense_route", id=expense_id))
        assert response.status_code == 404

    def test_delete_successful_deletion(self, app, auth_client):
        """A logged-in user deleting their own expense should succeed."""
        # 1. Identify the logged-in user
        with app.app_context():
            conn = sqlite3.connect(app.config["DATABASE"])
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE email = ?", ("test@example.com",)
            )
            user_id = cursor.fetchone()[0]
            conn.close()

        # 2. Seed an expense for this user
        expense_id = seed_expense(app, user_id)

        # 3. Delete the expense
        response = auth_client.get(url_for("delete_expense_route", id=expense_id))

        # 4. Verify redirect and flash message
        assert response.status_code == 302
        assert response.location == url_for("profile", )

        # Check flash message by following the redirect
        response_profile = auth_client.get(response.location)
        assert b"Expense deleted successfully!" in response_profile.data

        # 5. Verify DB side effect: expense should be gone
        with app.app_context():
            conn = sqlite3.connect(app.config["DATABASE"])
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
            result = cursor.fetchone()
            conn.close()
            assert result is None, "Expense should have been deleted from the database"
