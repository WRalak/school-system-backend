from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models import User

def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            if user.role != required_role and user.role != 'admin':
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return role_required('admin')(f)

def teacher_required(f):
    return role_required('teacher')(f)

def student_required(f):
    return role_required('student')(f)