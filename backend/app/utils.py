from functools import wraps
from flask import session, jsonify

def login_required(f):
    """
    Decorator to ensure a user is logged in.
    Checks if 'user_id' exists in the Flask session.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def role_required(allowed_roles):
    """
    Decorator to ensure the logged-in user has a specific role.
    Usage: @role_required(['staff'])
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # First, check if logged in
            if 'user_id' not in session:
                return jsonify({'error': 'Unauthorized', 'message': 'Authentication required'}), 401
            
            # Second, check role
            user_role = session.get('role')
            if user_role not in allowed_roles:
                return jsonify({
                    'error': 'Forbidden', 
                    'message': f'Role {user_role} is not authorized. Required: {allowed_roles}'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator