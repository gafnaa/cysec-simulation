from flask import Flask
from config import Config
from utils.xss_protection import xss_protection
import os

def register_template_filters(app):
    
    @app.template_filter('xss_safe')
    def xss_safe_filter(text):
        if text is None:
            return ""
        return xss_protection.sanitize_search_input(str(text))
    
    @app.template_filter('search_safe')
    def search_safe_filter(text):
        if text is None:
            return ""
        return xss_protection.sanitize_search_input(str(text))

def register_context_processors(app):
    @app.context_processor
    def security_helpers():
        return {
            'xss_protection': xss_protection,
            'is_potentially_malicious': xss_protection.is_potentially_malicious
        }

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    app.config.from_object(Config)
    app.debug = True  # Enable debug mode
    register_template_filters(app)
    register_context_processors(app)
    
    # Configure logging
    import logging
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)
    
    # Create upload directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('uploads/products', exist_ok=True)
    
    # Serve files from uploads directory
    from flask import send_from_directory
    
    @app.route('/uploads/products/<path:filename>')
    def serve_product_image(filename):
        directory = os.path.join(app.root_path, 'uploads/products')
        return send_from_directory(directory, filename)
    
    from routes.main import main_bp
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.chat import chat_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(chat_bp, url_prefix='/api')
    
    # Add global context processor for user data
    @app.context_processor
    def inject_user():
        from flask import session
        user_data = None
        if 'user_id' in session:
            from models.user import User
            user = User.find_by_id(session['user_id'])
            if user:
                user_data = user.to_dict()
        
        return dict(current_user=user_data)
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
