"""
Database initialization and test script
Run this to create tables and test database connection
"""
import sys
import os

# Ensure the backend directory is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from database import db
from models.user import User

def init_db():
    """Initialize database tables"""
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✓ Database tables created successfully!")
        
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@example.com').first()
        if not admin:
            print("\nCreating default admin user...")
            admin = User(
                name='Admin',
                email='admin@example.com',
                role='admin'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✓ Admin user created!")
            print("  Email: admin@example.com")
            print("  Password: admin123")
        else:
            print("\n✓ Admin user already exists")
        
        # Display statistics
        user_count = User.query.count()
        print("\nDatabase Statistics:")
        print(f"  Total users: {user_count}")
        print(f"  Admin users: {User.query.filter_by(role='admin').count()}")
        print(f"  Regular users: {User.query.filter_by(role='user').count()}")

if __name__ == '__main__':
    init_db()
