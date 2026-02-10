"""
Authentication Middleware
JWT token verification and role-based access control
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from jwt.exceptions import PyJWTError
from models.user import User


def jwt_required_custom(fn):
    """
    Custom JWT required decorator
    Verifies JWT token and attaches user to request context
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = int(get_jwt_identity())  # Convert string back to int
            
            # Get user from database
            user = User.query.get(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 404
            
            # Pass user to the route handler
            return fn(current_user=user, *args, **kwargs)
            
        except PyJWTError as e:
            return jsonify({
                'success': False,
                'message': f'Invalid or expired token: {str(e)}'
            }), 401
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Authentication error: {str(e)}'
            }), 401
    
    return wrapper


def admin_required(fn):
    """
    Admin role required decorator
    Must be used after @jwt_required_custom
    """
    @wraps(fn)
    def wrapper(*args, current_user=None, **kwargs):
        if not current_user:
            return jsonify({
                'success': False,
                'message': 'Authentication required'
            }), 401
        
        if current_user.role != 'admin':
            return jsonify({
                'success': False,
                'message': 'Admin access required'
            }), 403
        
        return fn(current_user=current_user, *args, **kwargs)
    
    return wrapper
