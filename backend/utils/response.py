"""
Response utility functions for consistent API responses
"""
from flask import jsonify


def success_response(message='Success', data=None, status_code=200):
    """
    Standard success response format
    """
    response = {
        'success': True,
        'message': message
    }
    
    if data is not None:
        response['data'] = data
    
    return jsonify(response), status_code


def error_response(message='Error occurred', status_code=400, errors=None):
    """
    Standard error response format
    """
    response = {
        'success': False,
        'message': message
    }
    
    if errors:
        response['errors'] = errors
    
    return jsonify(response), status_code


def paginated_response(data, page, limit, total, message='Success'):
    """
    Standard paginated response format
    """
    response = {
        'success': True,
        'message': message,
        'data': data,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'pages': (total + limit - 1) // limit  # Ceiling division
        }
    }
    
    return jsonify(response), 200
