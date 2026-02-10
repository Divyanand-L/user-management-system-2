"""
User Model - SQLAlchemy
Converted from Mongoose User schema
"""
from datetime import datetime
from database import db
import bcrypt


class User(db.Model):
    """User model for database"""
    
    __tablename__ = 'users'
    
    # Primary Key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # User Information
    name = db.Column(db.String(255), nullable=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    
    # Profile
    profile_image = db.Column(db.String(500), nullable=True, default=None)
    
    # Address Information
    address = db.Column(db.Text, nullable=True, default=None)
    state = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    pincode = db.Column(db.String(20), nullable=True)
    
    # Role
    role = db.Column(db.Enum('user', 'admin', name='user_roles'), default='user', nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def __init__(self, **kwargs):
        """Initialize user instance"""
        super(User, self).__init__(**kwargs)
        # Hash password if provided
        if 'password' in kwargs:
            self.set_password(kwargs['password'])
    
    def set_password(self, password):
        """Hash and set password"""
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    
    def to_dict(self, include_sensitive=False):
        """
        Convert user object to dictionary
        Excludes password by default
        Returns _id to match frontend MongoDB-style expectations
        """
        user_dict = {
            '_id': str(self.id),  # Frontend expects _id as string
            'id': self.id,  # Keep id for backward compatibility
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'profile_image': self.profile_image,
            'address': self.address,
            'state': self.state,
            'city': self.city,
            'country': self.country,
            'pincode': self.pincode,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            user_dict['password'] = self.password
        
        return user_dict
    
    def __repr__(self):
        return f'<User {self.email}>'
