"""
User Routes
"""
from flask import Blueprint

user_bp = Blueprint('users', __name__)

# Import controllers after blueprint creation
from controllers.user_controller import (
    get_all_users, get_user_by_id, get_current_user, 
    update_user, delete_user, update_role, update_role_by_email,
    upload_profile_image, delete_profile_image
)

# User routes
user_bp.route('', methods=['GET'])(get_all_users)  # Admin only - get all users
user_bp.route('/<int:user_id>', methods=['GET'])(get_user_by_id)  # Get specific user
user_bp.route('/me', methods=['GET'])(get_current_user)  # Get current user profile
user_bp.route('/me', methods=['PUT'])(update_user)  # Update current user's own profile
user_bp.route('/me', methods=['DELETE'])(delete_user)  # Delete current user's own account
user_bp.route('/<int:user_id>', methods=['PUT'])(update_user)  # Update user (admin or self)
user_bp.route('/<int:user_id>', methods=['DELETE'])(delete_user)  # Delete user (admin or self)
user_bp.route('/<int:user_id>/role', methods=['PATCH'])(update_role)  # Update role (admin only)
user_bp.route('/role/by-email', methods=['PATCH'])(update_role_by_email)  # Update role by email (admin only)

# Image routes
user_bp.route('/me/image', methods=['POST'])(upload_profile_image)  # Upload profile image
user_bp.route('/me/image', methods=['DELETE'])(delete_profile_image)  # Delete profile image
