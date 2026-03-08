def test_register(client):
    response = client.post('/api/auth/register', json={
        'username': 'newuser',
        'email': 'new@example.com',
        'password': 'password123',
        'first_name': 'New',
        'last_name': 'User',
        'role': 'student'
    })
    
    assert response.status_code == 201
    assert 'user_id' in response.json

def test_login(client):
    # First register a user
    client.post('/api/auth/register', json={
        'username': 'loginuser',
        'email': 'login@example.com',
        'password': 'password123',
        'first_name': 'Login',
        'last_name': 'User'
    })
    
    # Then try to login
    response = client.post('/api/auth/login', json={
        'username': 'loginuser',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_login_invalid_credentials(client):
    response = client.post('/api/auth/login', json={
        'username': 'nonexistent',
        'password': 'wrongpass'
    })
    
    assert response.status_code == 401
    assert 'error' in response.json