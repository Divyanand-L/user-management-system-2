"""
Authentication Routes
"""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

# Import controllers after blueprint creation to avoid circular imports
from controllers.auth_controller import register, login, logout, refresh_access_token

# Register routes
auth_bp.route('/register', methods=['POST'])(register)
auth_bp.route('/login', methods=['POST'])(login)
auth_bp.route('/logout', methods=['POST'])(logout)
auth_bp.route('/refresh', methods=['POST'])(refresh_access_token)
