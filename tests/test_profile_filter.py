import pytest
from unittest.mock import patch
from app import app as flask_app
from database.db import init_db, get_db
import database.queries

@pytest.fixture
def app():
    import os
    db_file = "test_spendly.db"
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': db_file,
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })
    with flask_app.app_context():
        init_db()
        yield flask_app
    # Cleanup test database
    if os.path.exists(db_file):
        os.remove(db_file)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    """A test client that is already logged in."""
    client.post('/register', data={'name': 'Test User', 'email': 'test@example.com', 'password': 'testpass'})
    client.post('/login', data={'email': 'test@example.com', 'password': 'testpass'})
    return client

@pytest.fixture
def seeded_expenses(auth_client):
    """Seeds expenses for the logged-in user across different dates."""
    with flask_app.app_context():
        conn = get_db()

        # Find the user ID for the registered test user
        user = conn.execute("SELECT id FROM users WHERE email = ?", ('test@example.com',)).fetchone()
        user_id = user['id']

        expenses = [
            ('2023-01-01', 'Grocery', 'Food', 10.0),
            ('2023-02-01', 'Bus', 'Transport', 20.0),
            ('2023-03-01', 'Movie', 'Entertainment', 30.0),
        ]
        for date, desc, cat, amt in expenses:
            conn.execute(
                "INSERT INTO expenses (user_id, date, description, category, amount) VALUES (?, ?, ?, ?, ?)",
                (user_id, date, desc, cat, amt)
            )
        conn.commit()

class TestProfileDateFilter:

    def test_profile_no_filters(self, auth_client, seeded_expenses):
        """1. Basic profile page loading without filters."""
        with patch('app.get_summary_stats', wraps=database.queries.get_summary_stats) as mock_stats:
            response = auth_client.get('/profile')

            assert response.status_code == 200
            # Verify call: (user_id, start_date=None, end_date=None)
            args, kwargs = mock_stats.call_args
            assert args[1] is None
            assert args[2] is None

            # Total should be 60.0 (10+20+30)
            assert b"60.0" in response.data
            assert b"Grocery" in response.data
            assert b"Movie" in response.data

    def test_profile_filter_start_date(self, auth_client, seeded_expenses):
        """2. Filtering by start_date only."""
        start_date = '2023-02-01'
        with patch('app.get_summary_stats', wraps=database.queries.get_summary_stats) as mock_stats:
            response = auth_client.get(f'/profile?start_date={start_date}')

            assert response.status_code == 200
            # Verify call
            args, kwargs = mock_stats.call_args
            assert args[1] == start_date
            assert args[2] is None

            # Total should be 50.0 (20+30)
            assert b"50.0" in response.data
            assert b"Grocery" not in response.data # Jan 1st is filtered out

    def test_profile_filter_end_date(self, auth_client, seeded_expenses):
        """3. Filtering by end_date only."""
        end_date = '2023-02-15'
        with patch('app.get_summary_stats', wraps=database.queries.get_summary_stats) as mock_stats:
            response = auth_client.get(f'/profile?end_date={end_date}')

            assert response.status_code == 200
            # Verify call
            args, kwargs = mock_stats.call_args
            assert args[1] is None
            assert args[2] == end_date

            # Total should be 30.0 (10+20)
            assert b"30.0" in response.data
            assert b"Movie" not in response.data # Mar 1st is filtered out

    def test_profile_filter_date_range(self, auth_client, seeded_expenses):
        """4. Filtering by both start_date and end_date."""
        start = '2023-01-15'
        end = '2023-02-15'
        with patch('app.get_summary_stats', wraps=database.queries.get_summary_stats) as mock_stats:
            response = auth_client.get(f'/profile?start_date={start}&end_date={end}')

            assert response.status_code == 200
            # Verify call
            args, kwargs = mock_stats.call_args
            assert args[1] == start
            assert args[2] == end

            # Only Feb transaction matches: 20.0
            assert b"20.0" in response.data
            assert b"Grocery" not in response.data
            assert b"Movie" not in response.data

    def test_profile_filter_no_data(self, auth_client, seeded_expenses):
        """5. Handling of date ranges with no data."""
        start = '2099-01-01'
        response = auth_client.get(f'/profile?start_date={start}')

        assert response.status_code == 200
        assert b"0.0" in response.data # Total spent
        assert b"0" in response.data # Transaction count
        # Use a more robust check for the placeholder since it's a non-ASCII character
        assert "—" in response.data.decode('utf-8', errors='ignore') # Top category placeholder

    def test_profile_clear_filter(self, auth_client, seeded_expenses):
        """6. 'Clear Filter' functionality."""
        # Apply a filter first
        auth_client.get('/profile?start_date=2023-02-01')

        # Simulate clicking 'Clear Filter' link which redirects back to /profile
        response = auth_client.get('/profile')

        assert response.status_code == 200
        # Should show all data again
        assert b"60.0" in response.data

    def test_profile_filter_persistence(self, auth_client, seeded_expenses):
        """7. Persistence of filter values in the form."""
        start = '2023-01-01'
        end = '2023-12-31'
        response = auth_client.get(f'/profile?start_date={start}&end_date={end}')

        assert response.status_code == 200
        # Check if the input fields contain the provided values
        assert f'value="{start}"'.encode() in response.data
        assert f'value="{end}"'.encode() in response.data
