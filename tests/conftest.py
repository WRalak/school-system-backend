import pytest
from app import create_app
from extensions import db
from models import User

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    # Create test user
    user = User(
        username='testuser',
        email='test@example.com',
        first_name='Test',
        last_name='User',
        role='admin'
    )
    user.set_password('password123')
    
    with client.application.app_context():
        db.session.add(user)
        db.session.commit()
    
    # Login and get token
    response = client.post('/api/auth/login', json={
        'username': 'testuser',
        'password': 'password123'
    })
    
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}