import pytest
import json
from real_backend import app as flask_app

# --- Fixtures ---
@pytest.fixture(scope='module')
def app():
    flask_app.config.update({
        "TESTING": True,
        # "SECRET_KEY": "test_secret_key", # Example: Override if needed
        # "JWT_SECRET_KEY": "test_jwt_secret_key", # Example: Override if needed
    })
    # In a real-world scenario, you might initialize a test database here
    # with flask_app.app_context():
    #     # from setup_database import init_test_db
    #     # init_test_db()
    #     pass
    yield flask_app
    # Teardown test database if created
    # with flask_app.app_context():
    #     # from setup_database import drop_test_db
    #     # drop_test_db()
    #     pass

@pytest.fixture(scope='module')
def client(app):
    return app.test_client()

# --- Test Cases ---

def test_health_check_api(client):
    """Test the /api/health endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    try:
        data = response.get_json()
    except Exception as e:
        pytest.fail(f"Failed to parse JSON from /api/health: {e}\nResponse data: {response.data.decode()}")

    assert data['status'] == 'healthy'
    assert 'database' in data
    assert 'deepseek_ai' in data
    assert 'timestamp' in data

def test_stats_api_basic_structure(client):
    """Test the basic structure of /api/stats endpoint."""
    response = client.get('/api/stats')
    assert response.status_code == 200
    try:
        data = response.get_json()
    except Exception as e:
        pytest.fail(f"Failed to parse JSON from /api/stats: {e}\nResponse data: {response.data.decode()}")

    expected_keys = [
        'total_conversations', 'active_users_today', 'total_distinct_users',
        'messages_today', 'response_time', 'satisfaction_rate',
        'channels_today', 'hourly_stats_today', 'recent_chats'
    ]
    for key in expected_keys:
        assert key in data, f"Key '{key}' missing in /api/stats response"
    assert isinstance(data['recent_chats'], list)

def test_chat_api_basic_message(client):
    """Test sending a basic message to /api/chat."""
    payload = {
        "message": "Hello pytest from chat",
        "user_id": "pytest_user_chat",
        "session_id": "pytest_session_chat"
    }
    response = client.post('/api/chat', json=payload)
    assert response.status_code == 200
    try:
        data = response.get_json()
    except Exception as e:
        pytest.fail(f"Failed to parse JSON from /api/chat: {e}\nResponse data: {response.data.decode()}")

    assert data['success'] is True
    assert 'response' in data
    assert data['user_id'] == payload['user_id']

# --- Authentication Tests ---
# Assuming 'admin' with password 'SecureAdmin123!' is set up by setup_database.py
VALID_USERNAME = "admin"
VALID_PASSWORD = "SecureAdmin123!"
INVALID_PASSWORD = "wrong_test_password"

def test_login_api_success(client):
    """Test successful login to /api/auth/login."""
    credentials = {"username": VALID_USERNAME, "password": VALID_PASSWORD}
    response = client.post('/api/auth/login', json=credentials)
    assert response.status_code == 200
    try:
        data = response.get_json()
    except Exception as e:
        pytest.fail(f"Failed to parse JSON from successful /api/auth/login: {e}\nResponse data: {response.data.decode()}")

    assert data['success'] is True
    assert 'token' in data
    assert 'user' in data
    assert data['user']['username'] == VALID_USERNAME

def test_login_api_failure_wrong_password(client):
    """Test failed login with wrong password."""
    credentials = {"username": VALID_USERNAME, "password": INVALID_PASSWORD}
    response = client.post('/api/auth/login', json=credentials)
    assert response.status_code == 401  # Unauthorized
    try:
        data = response.get_json()
    except Exception as e:
        pytest.fail(f"Failed to parse JSON from failed /api/auth/login (wrong_password): {e}\nResponse data: {response.data.decode()}")

    assert data['success'] is False
    assert 'error' in data

def test_login_api_failure_missing_username(client):
    """Test failed login with missing username."""
    credentials = {"password": VALID_PASSWORD}
    response = client.post('/api/auth/login', json=credentials)
    assert response.status_code == 400  # Bad Request
    try:
        data = response.get_json()
    except Exception as e:
        pytest.fail(f"Failed to parse JSON from failed /api/auth/login (missing_username): {e}\nResponse data: {response.data.decode()}")

    assert data['success'] is False
    assert 'error' in data

def test_login_api_failure_missing_password(client):
    """Test failed login with missing password."""
    credentials = {"username": VALID_USERNAME}
    response = client.post('/api/auth/login', json=credentials)
    assert response.status_code == 400  # Bad Request
    try:
        data = response.get_json()
    except Exception as e:
        pytest.fail(f"Failed to parse JSON from failed /api/auth/login (missing_password): {e}\nResponse data: {response.data.decode()}")

    assert data['success'] is False
    assert 'error' in data

# Placeholder for testing protected routes
# def test_access_protected_route_example(client):
#     # Step 1: Login to get a token
#     login_payload = {"username": VALID_USERNAME, "password": VALID_PASSWORD}
#     login_response = client.post('/api/auth/login', json=login_payload)
#     token = login_response.get_json().get('token')
#     assert token is not None
#
#     # Step 2: Access a protected route with the token
#     # Assuming '/api/some_protected_endpoint' requires authentication
#     # headers = {'Authorization': f'Bearer {token}'}
#     # protected_response = client.get('/api/some_protected_endpoint', headers=headers)
#     # assert protected_response.status_code == 200
#     pass
#
# def test_access_protected_route_without_token_example(client):
#     # protected_response = client.get('/api/some_protected_endpoint')
#     # assert protected_response.status_code == 401 # Or 403 depending on implementation
#     pass
