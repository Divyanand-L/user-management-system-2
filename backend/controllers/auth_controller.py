"""
Authentication Controller
Handles user registration, login, logout, token refresh
"""
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from database import db
from models.user import User
from utils.response import success_response, error_response
from middleware.auth import jwt_required_custom


def register():
    """Register a new user (supports both JSON and FormData)"""
    try:
        # Support both JSON and FormData (for file uploads)
        if request.is_json:
            data = request.get_json()
        else:
            # FormData from frontend
            data = request.form.to_dict()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return error_response(f'{field} is required', 400)
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            return error_response('Email already registered', 400)
        
        # Create new user
        new_user = User(
            name=data['name'],
            email=data['email'],
            phone=data.get('phone'),
            address=data.get('address'),
            state=data.get('state'),
            city=data.get('city'),
            country=data.get('country'),
            pincode=data.get('pincode'),
            role=data.get('role', 'user')
        )
        new_user.set_password(data['password'])
        
        # Handle profile image upload if provided
        profile_image_url = None
        if 'profile_image' in request.files:
            from utils.cloudinary_helper import upload_image_to_cloudinary
            file = request.files['profile_image']
            
            if file and file.filename:
                # Save user first to get ID
                db.session.add(new_user)
                db.session.flush()  # Get ID without committing
                
                # Upload to Cloudinary
                upload_result = upload_image_to_cloudinary(file, new_user.id)
                
                if upload_result['success']:
                    profile_image_url = upload_result['url']
                    new_user.profile_image = profile_image_url
                # If upload fails, continue without image (don't fail registration)
        
        db.session.add(new_user)
        db.session.commit()
        
        # Generate tokens (convert ID to string for JWT)
        access_token = create_access_token(identity=str(new_user.id))
        refresh_token_str = create_refresh_token(identity=str(new_user.id))
        
        return success_response(
            message='User registered successfully',
            data={
                'user': new_user.to_dict(),
                'tokens': {
                    'accessToken': access_token,
                    'refreshToken': refresh_token_str
                }
            },
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f'Registration failed: {str(e)}', 500)


def login():
    """Login user"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('email') and not data.get('phone'):
            return error_response('Email or phone is required', 400)
        
        if not data.get('password'):
            return error_response('Password is required', 400)
        
        # Find user by email or phone
        user = None
        if data.get('email'):
            user = User.query.filter_by(email=data['email']).first()
        elif data.get('phone'):
            user = User.query.filter_by(phone=data['phone']).first()
        
        if not user:
            return error_response('Invalid credentials', 401)
        
        # Verify password
        if not user.check_password(data['password']):
            return error_response('Invalid credentials', 401)
        
        # Generate tokens (convert ID to string for JWT)
        access_token = create_access_token(identity=str(user.id))
        refresh_token_str = create_refresh_token(identity=str(user.id))
        
        return success_response(
            message='Login successful',
            data={
                'user': user.to_dict(),
                'tokens': {
                    'accessToken': access_token,
                    'refreshToken': refresh_token_str
                }
            }
        )
        
    except Exception as e:
        return error_response(f'Login failed: {str(e)}', 500)


@jwt_required_custom
def logout(current_user=None):
    """Logout user (client-side token removal)"""
    return success_response(message='Logout successful')


def refresh_access_token():
    """
    Refresh access token using refresh token
    Supports both methods:
    1. Frontend style: { "refreshToken": "..." } in request body
    2. Test style: Authorization header with Bearer token
    """
    try:
        from flask_jwt_extended import decode_token
        
        refresh_token = None
        
        # Try to get refresh token from request body (frontend method)
        data = request.get_json(silent=True)
        if data and data.get('refreshToken'):
            refresh_token = data.get('refreshToken')
        else:
            # Try Authorization header (test method)
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                refresh_token = auth_header.split(' ')[1]
        
        if not refresh_token:
            return error_response('Refresh token is required in body or Authorization header', 400)
        
        # Decode and verify the refresh token
        try:
            decoded_token = decode_token(refresh_token)
            user_id = int(decoded_token['sub'])  # Convert string back to int
        except Exception as decode_error:
            return error_response(f'Invalid refresh token: {str(decode_error)}', 401)
        
        # Verify user still exists
        user = User.query.get(user_id)
        if not user:
            return error_response('User not found', 404)
        
        # Generate new tokens (convert ID to string for JWT)
        # Implement token rotation: issue both new access and refresh tokens
        new_access_token = create_access_token(identity=str(user_id))
        new_refresh_token = create_refresh_token(identity=str(user_id))
        
        return success_response(
            message='Token refreshed successfully',
            data={
                'tokens': {
                    'accessToken': new_access_token,
                    'refreshToken': new_refresh_token
                }
            }
        )
        
    except Exception as e:
        return error_response(f'Token refresh failed: {str(e)}', 401)
