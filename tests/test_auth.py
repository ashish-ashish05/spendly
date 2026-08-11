import pytest
from app import app
from database.db import init_db, seed_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret'
    with app.test_client() as client:
        with app.app_context():
            init_db()
            seed_db()
        yield client

def test_login_success(client):
    # Using the demo user from seed_db
    response = client.post('/login', data={
        'email': 'demo@spendly.com',
        'password': 'demo123'
    }, follow_redirects=True)

    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert 'user_id' in sess

def test_login_failure_password(client):
    response = client.post('/login', data={
        'email': 'demo@spendly.com',
        'password': 'wrongpassword'
    }, follow_redirects=True)

    assert b"Invalid email or password" in response.data
    with client.session_transaction() as sess:
        assert 'user_id' not in sess

def test_login_failure_email(client):
    response = client.post('/login', data={
        'email': 'nonexistent@example.com',
        'password': 'demo123'
    }, follow_redirects=True)

    assert b"Invalid email or password" in response.data
    with client.session_transaction() as sess:
        assert 'user_id' not in sess

def test_logout_success(client):
    # Log in first
    client.post('/login', data={
        'email': 'demo@spendly.com',
        'password': 'demo123'
    })

    # Log out
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as sess:
        assert 'user_id' not in sess

def test_logout_anonymous(client):
    # Attempt logout without being logged in
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    # Should redirect to login
    assert 'login' in response.request.path or response.request.url.path == '/login'

def test_authenticated_user_cannot_access_auth_pages(client):
    # Log in
    client.post('/login', data={
        'email': 'demo@spendly.com',
        'password': 'demo123'
    })

    # Try to access /login
    response_login = client.get('/login', follow_redirects=True)
    assert response_login.status_code == 200
    # Should be redirected to landing page
    assert response_login.request.path == '/'

    # Try to access /register
    response_reg = client.get('/register', follow_redirects=True)
    assert response_reg.status_code == 200
    # Should be redirected to landing page
    assert response_reg.request.path == '/'
