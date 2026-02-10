"""
User Controller - Enhanced with Cloudinary image uploads
Handles user CRUD operations, profile management, and image uploads
"""
from flask import request
from sqlalchemy import or_
from database import db
from models.user import User
from utils.response import success_response, error_response, paginated_response
from utils.cloudinary_helper import upload_image_to_cloudinary, delete_image_from_cloudinary, extract_public_id_from_url
from middleware.auth import jwt_required_custom, admin_required


@jwt_required_custom
@admin_required
def get_all_users(current_user=None):
    """Get all users with pagination, search, and filtering (Admin only)"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        search = request.args.get('search', '', type=str)
        role = request.args.get('role', '', type=str)
        
        # Build query
        query = User.query
        
        # Apply search filter
        if search:
            search_filter = or_(
                User.name.like(f'%{search}%'),
                User.email.like(f'%{search}%'),
                User.phone.like(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # Apply role filter
        if role in ['user', 'admin']:
            query = query.filter_by(role=role)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        users = query.offset((page - 1) * limit).limit(limit).all()
        
        # Convert to dict
        users_data = [user.to_dict() for user in users]
        
        return paginated_response(users_data, page, limit, total, 'Users retrieved successfully')
        
    except Exception as e:
        return error_response(f'Failed to retrieve users: {str(e)}', 500)


@jwt_required_custom
def get_user_by_id(current_user=None, user_id=None):
    """Get user by ID"""
    try:
        # Only admin or the user themselves can view
        if current_user.role != 'admin' and current_user.id != user_id:
            return error_response('Access denied', 403)
        
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found', 404)
        
        return success_response(
            message='User retrieved successfully',
            data={'user': user.to_dict()}
        )
        
    except Exception as e:
        return error_response(f'Failed to retrieve user: {str(e)}', 500)


@jwt_required_custom
def get_current_user(current_user=None):
    """Get current logged-in user profile"""
    try:
        return success_response(
            message='Profile retrieved successfully',
            data={'user': current_user.to_dict()}
        )
    except Exception as e:
        return error_response(f'Failed to retrieve profile: {str(e)}', 500)


@jwt_required_custom
def update_user(current_user=None, user_id=None):
    """Update user information including profile image"""
    try:
        # If user_id is None, user is updating themselves (/me route)
        if user_id is None:
            user = current_user
        else:
            # Only admin or the user themselves can update
            if current_user.role != 'admin' and current_user.id != user_id:
                return error_response('Access denied', 403)
            
            user = User.query.get(user_id)
            if not user:
                return error_response('User not found', 404)
        
        # Handle multipart form data (for file uploads)
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = request.form.to_dict()
            
            # Handle profile image upload
            if 'profile_image' in request.files:
                file = request.files['profile_image']
                if file and file.filename:
                    # Delete old image if exists
                    if user.profile_image:
                        old_public_id = extract_public_id_from_url(user.profile_image)
                        if old_public_id:
                            delete_image_from_cloudinary(old_public_id)
                    
                    # Upload new image
                    upload_result = upload_image_to_cloudinary(file, user_id)
                    if upload_result['success']:
                        user.profile_image = upload_result['url']
                    else:
                        return error_response(upload_result['error'], 400)
        else:
            # Handle JSON data
            data = request.get_json() or {}
        
        # Update allowed fields
        allowed_fields = ['name', 'phone', 'address', 'state', 'city', 'country', 'pincode']
        for field in allowed_fields:
            if field in data and data[field] is not None:
                setattr(user, field, data[field])
        
        # Update password if provided
        if 'password' in data and data['password']:
            user.set_password(data['password'])
        
        # Only admin can update role
        if 'role' in data and current_user.role == 'admin':
            if data['role'] in ['user', 'admin']:
                user.role = data['role']
        
        db.session.commit()
        
        return success_response(
            message='User updated successfully',
            data={'user': user.to_dict()}
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update user: {str(e)}', 500)


@jwt_required_custom
def delete_user(current_user=None, user_id=None):
    """Delete user account and associated Cloudinary image"""
    try:
        # If user_id is None, user is deleting themselves (/me route)
        if user_id is None:
            user = current_user
        else:
            # Only admin or the user themselves can delete
            if current_user.role != 'admin' and current_user.id != user_id:
                return error_response('Access denied', 403)
            
            user = User.query.get(user_id)
            if not user:
                return error_response('User not found', 404)
        
        # Delete profile image from Cloudinary if exists
        if user.profile_image:
            public_id = extract_public_id_from_url(user.profile_image)
            if public_id:
                delete_image_from_cloudinary(public_id)
        
        db.session.delete(user)
        db.session.commit()
        
        return success_response(message='User deleted successfully')
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete user: {str(e)}', 500)


@jwt_required_custom
@admin_required
def update_role(current_user=None, user_id=None):
    """Update user role (Admin only)"""
    try:
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found', 404)
        
        data = request.get_json()
        new_role = data.get('role')
        
        if new_role not in ['user', 'admin']:
            return error_response('Invalid role. Must be "user" or "admin"', 400)
        
        user.role = new_role
        db.session.commit()
        
        return success_response(
            message=f'User role updated to {new_role}',
            data={'user': user.to_dict()}
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update role: {str(e)}', 500)


@jwt_required_custom
@admin_required
def update_role_by_email(current_user=None):
    """Update user role by email (Admin only)"""
    try:
        data = request.get_json()
        email = data.get('email')
        new_role = data.get('role')
        
        if not email:
            return error_response('Email is required', 400)
        
        if new_role not in ['user', 'admin']:
            return error_response('Invalid role. Must be "user" or "admin"', 400)
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        if not user:
            return error_response(f'User with email {email} not found', 404)
        
        # Update role
        old_role = user.role
        user.role = new_role
        db.session.commit()
        
        return success_response(
            message=f'User {user.name} ({email}) role updated from {old_role} to {new_role}',
            data={'user': user.to_dict()}
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update role: {str(e)}', 500)


@jwt_required_custom
def upload_profile_image(current_user=None):
    """Upload or update profile image"""
    try:
        if 'image' not in request.files:
            return error_response('No image file provided', 400)
        
        file = request.files['image']
        if not file or not file.filename:
            return error_response('No image file provided', 400)
        
        # Delete old image if exists
        if current_user.profile_image:
            old_public_id = extract_public_id_from_url(current_user.profile_image)
            if old_public_id:
                delete_image_from_cloudinary(old_public_id)
        
        # Upload new image
        upload_result = upload_image_to_cloudinary(file, current_user.id)
        
        if not upload_result['success']:
            return error_response(upload_result['error'], 400)
        
        # Update user profile image URL
        current_user.profile_image = upload_result['url']
        db.session.commit()
        
        return success_response(
            message='Profile image uploaded successfully',
            data={
                'user': current_user.to_dict(),
                'image_url': upload_result['url']
            }
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to upload image: {str(e)}', 500)


@jwt_required_custom
def delete_profile_image(current_user=None):
    """Delete profile image"""
    try:
        if not current_user.profile_image:
            return error_response('No profile image to delete', 400)
        
        # Delete from Cloudinary
        public_id = extract_public_id_from_url(current_user.profile_image)
        if public_id:
            delete_result = delete_image_from_cloudinary(public_id)
            if not delete_result['success']:
                return error_response(delete_result['error'], 400)
        
        # Remove from database
        current_user.profile_image = None
        db.session.commit()
        
        return success_response(
            message='Profile image deleted successfully',
            data={'user': current_user.to_dict()}
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to delete image: {str(e)}', 500)
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Failed to update role: {str(e)}', 500)
