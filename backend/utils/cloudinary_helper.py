"""
Cloudinary Image Upload Utility
Handles image uploads to Cloudinary cloud storage
"""
import cloudinary.uploader
from flask import current_app
from werkzeug.utils import secure_filename
import os


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def upload_image_to_cloudinary(file, user_id):
    """
    Upload image to Cloudinary
    
    Args:
        file: FileStorage object from request.files
        user_id: ID of the user (for naming)
    
    Returns:
        dict: {'success': bool, 'url': str or None, 'error': str or None}
    """
    try:
        # Validate file
        if not file:
            return {'success': False, 'url': None, 'error': 'No file provided'}
        
        if not allowed_file(file.filename):
            return {
                'success': False, 
                'url': None, 
                'error': f'Invalid file type. Allowed: {", ".join(current_app.config["ALLOWED_EXTENSIONS"])}'
            }
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        
        if file_length > current_app.config['MAX_FILE_SIZE']:
            max_mb = current_app.config['MAX_FILE_SIZE'] / (1024 * 1024)
            return {
                'success': False,
                'url': None,
                'error': f'File too large. Maximum size: {max_mb}MB'
            }
        
        # Generate unique public_id
        filename = secure_filename(file.filename)
        public_id = f"user_{user_id}_{filename.rsplit('.', 1)[0]}"
        
        # Upload to Cloudinary
        upload_result = cloudinary.uploader.upload(
            file,
            folder=current_app.config['CLOUDINARY_FOLDER'],
            public_id=public_id,
            overwrite=True,
            resource_type='image',
            transformation=[
                {'width': 500, 'height': 500, 'crop': 'limit'},
                {'quality': 'auto'},
                {'fetch_format': 'auto'}
            ]
        )
        
        return {
            'success': True,
            'url': upload_result['secure_url'],
            'public_id': upload_result['public_id'],
            'error': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'url': None,
            'error': f'Upload failed: {str(e)}'
        }


def delete_image_from_cloudinary(public_id):
    """
    Delete image from Cloudinary
    
    Args:
        public_id: Cloudinary public_id of the image
    
    Returns:
        dict: {'success': bool, 'error': str or None}
    """
    try:
        if not public_id:
            return {'success': True, 'error': None}  # Nothing to delete
        
        result = cloudinary.uploader.destroy(public_id)
        
        return {
            'success': True,
            'error': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Delete failed: {str(e)}'
        }


def extract_public_id_from_url(cloudinary_url):
    """
    Extract public_id from Cloudinary URL
    
    Args:
        cloudinary_url: Full Cloudinary URL
    
    Returns:
        str: public_id or None
    """
    try:
        if not cloudinary_url or 'cloudinary.com' not in cloudinary_url:
            return None
        
        # Extract public_id from URL
        # Format: https://res.cloudinary.com/{cloud_name}/image/upload/v{version}/{public_id}.{format}
        parts = cloudinary_url.split('/upload/')
        if len(parts) < 2:
            return None
        
        # Get the part after 'upload/'
        path = parts[1]
        # Remove version number if present (v1234567890/)
        if path.startswith('v'):
            path = '/'.join(path.split('/')[1:])
        
        # Remove file extension
        public_id = path.rsplit('.', 1)[0]
        
        return public_id
        
    except Exception:
        return None
