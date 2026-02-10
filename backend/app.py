"""
Main Flask Application Entry Point
"""
import os
from flask import Flask
from flask_cors import CORS
from config import config
import cloudinary

# Import extensions from database module
from database import db, migrate, jwt


def create_app(config_name=None):
    """
    Application factory pattern
    """
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # Initialize Cloudinary
    if app.config['CLOUDINARY_CLOUD_NAME']:
        cloudinary.config(
            cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
            api_key=app.config['CLOUDINARY_API_KEY'],
            api_secret=app.config['CLOUDINARY_API_SECRET']
        )
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'ok', 'message': 'Server is running'}, 200
    
    @app.route('/', methods=['GET'])
    def index():
        return {
            'message': 'User Management System API',
            'version': '1.0.0',
            'endpoints': {
                'auth': '/api/auth',
                'users': '/api/users',
                'health': '/health'
            }
        }, 200
    
    return app


def register_blueprints(flask_app):
    """Register Flask blueprints"""
    from routes.auth_routes import auth_bp
    from routes.user_routes import user_bp
    
    flask_app.register_blueprint(auth_bp, url_prefix='/api/auth')
    flask_app.register_blueprint(user_bp, url_prefix='/api/users')


def register_error_handlers(flask_app):
    """Register error handlers"""
    
    @flask_app.errorhandler(404)
    def not_found(_error):
        return {'success': False, 'message': 'Resource not found'}, 404
    
    @flask_app.errorhandler(500)
    def internal_server_error(_error):
        return {'success': False, 'message': 'Internal server error'}, 500
    
    @flask_app.errorhandler(Exception)
    def handle_exception(error):
        flask_app.logger.error(f'Unhandled exception: {str(error)}')
        return {'success': False, 'message': 'An error occurred'}, 500


if __name__ == '__main__':
    flask_app = create_app()
    flask_app.run(
        host=flask_app.config['HOST'],
        port=flask_app.config['PORT'],
        debug=flask_app.config['DEBUG']
    )
