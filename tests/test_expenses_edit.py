import pytest
from app import app as flask_app
from database.db import init_db, create_user
from database.queries import add_expense, get_expense_by_id


@pytest.fixture
def app():
    flask_app.config.update(
        {
            "TESTING": True,
            "DATABASE": "test_spendly.db",
            "SECRET_KEY": "test-secret",
            "WTF_CSRF_ENABLED": False,
        }
    )
    with flask_app.app_context():
        init_db()
        yield flask_app
        # Cleanup test database after tests
        import os

        if os.path.exists("test_spendly.db"):
            os.remove("test_spendly.db")


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    client.post(
        "/register",
        data={"name": "testuser", "email": "test@example.com", "password": "testpass"},
    )
    client.post("/login", data={"email": "test@example.com", "password": "testpass"})
    return client


@pytest.fixture
def setup_expense(app, auth_client):
    """Helper to create an expense for the logged-in user and return its ID."""
    with app.app_context():
        from database.db import get_db

        db = get_db()
        user = db.execute(
            "SELECT id FROM users WHERE email = 'test@example.com'"
        ).fetchone()
        user_id = user["id"]

        add_expense(user_id, 100.0, "Food", "2023-10-01", "Test Lunch")

        # Fetch the ID of the expense we just created
        expense = db.execute(
            "SELECT id FROM expenses ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return expense["id"]


class TestEditExpense:

    def test_edit_get_unauthorized(self, client):
        """Accessing edit page without login should redirect to login."""
        response = client.get("/expenses/1/edit")
        assert response.status_code == 302
        assert "/login" in response.location

    def test_edit_get_not_found(self, auth_client):
        """Accessing a non-existent expense ID should return 404."""
        response = auth_client.get("/expenses/9999/edit")
        assert response.status_code == 404

    def test_edit_get_not_owner(self, auth_client, app):
        """Accessing another user's expense should return 404."""
        with app.app_context():
            from database.db import get_db

            db = get_db()
            # Create second user
            db.execute(
                "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, datetime('now'))",
                ("Other", "other@example.com", "hash"),
            )
            db.commit()
            other_user = db.execute(
                "SELECT id FROM users WHERE email = 'other@example.com'"
            ).fetchone()

            # Create expense for other user
            add_expense(other_user["id"], 50.0, "Travel", "2023-10-02", "Other Trip")
            expense = db.execute(
                "SELECT id FROM expenses ORDER BY id DESC LIMIT 1"
            ).fetchone()
            expense_id = expense["id"]

            response = auth_client.get(f"/expenses/{expense_id}/edit")
            assert response.status_code == 404

    def test_edit_get_success(self, auth_client, setup_expense):
        """Editing own expense should show pre-filled form."""
        expense_id = setup_expense
        response = auth_client.get(f"/expenses/{expense_id}/edit")

        assert response.status_code == 200
        assert b"Edit Expense" in response.data
        # Check pre-filled values
        assert b"100.0" in response.data
        assert b"Food" in response.data
        assert b"2023-10-01" in response.data
        assert b"Test Lunch" in response.data

    def test_edit_post_unauthorized(self, client):
        """Updating without login should redirect to login."""
        response = client.post("/expenses/1/edit", data={"amount": "200"})
        assert response.status_code == 302
        assert "/login" in response.location

    def test_edit_post_not_owner(self, auth_client, app):
        """Updating another user's expense should return 404."""
        with app.app_context():
            from database.db import get_db

            db = get_db()
            db.execute(
                "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, datetime('now'))",
                ("Other", "other@example.com", "hash"),
            )
            db.commit()
            other_user = db.execute(
                "SELECT id FROM users WHERE email = 'other@example.com'"
            ).fetchone()
            add_expense(other_user["id"], 50.0, "Travel", "2023-10-02", "Other Trip")
            expense_id = db.execute(
                "SELECT id FROM expenses ORDER BY id DESC LIMIT 1"
            ).fetchone()["id"]

            response = auth_client.post(
                f"/expenses/{expense_id}/edit",
                data={
                    "amount": "60",
                    "category": "Travel",
                    "date": "2023-10-02",
                    "description": "Updated",
                },
            )
            assert response.status_code == 404

    @pytest.mark.parametrize(
        "payload, error_text",
        [
            (
                {"amount": "", "category": "Food", "date": "2023-10-01"},
                "Amount, category, and date are required",
            ),
            (
                {"amount": "100", "category": "", "date": "2023-10-01"},
                "Amount, category, and date are required",
            ),
            (
                {"amount": "100", "category": "Food", "date": ""},
                "Amount, category, and date are required",
            ),
            (
                {"amount": "-10", "category": "Food", "date": "2023-10-01"},
                "Amount must be a positive number",
            ),
            (
                {"amount": "abc", "category": "Food", "date": "2023-10-01"},
                "Amount must be a valid number",
            ),
        ],
    )
    def test_edit_post_validation_errors(
        self, auth_client, setup_expense, payload, error_text
    ):
        """Invalid inputs should return form with error message."""
        expense_id = setup_expense
        response = auth_client.post(f"/expenses/{expense_id}/edit", data=payload)

        assert response.status_code == 200
        assert error_text.encode() in response.data

    def test_edit_post_success(self, auth_client, setup_expense, app):
        """Valid update should persist to DB and redirect to profile."""
        expense_id = setup_expense
        new_data = {
            "amount": "150.50",
            "category": "Entertainment",
            "date": "2023-11-01",
            "description": "Movie Night",
        }

        response = auth_client.post(f"/expenses/{expense_id}/edit", data=new_data)

        # Verify redirect
        assert response.status_code == 302
        assert "/profile" in response.location

        # Verify DB update
        with app.app_context():
            updated_expense = get_expense_by_id(expense_id)
            assert updated_expense["amount"] == 150.50
            assert updated_expense["category"] == "Entertainment"
            assert updated_expense["date"] == "2023-11-01"
            assert updated_expense["description"] == "Movie Night"
