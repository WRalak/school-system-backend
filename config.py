import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Force SQLite for development - use absolute path
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'school.db')
    
    # Ignore any DATABASE_URL environment variable that might be set
    # SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///school.db')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')