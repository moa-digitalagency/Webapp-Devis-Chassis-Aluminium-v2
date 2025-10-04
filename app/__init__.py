from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os

db = SQLAlchemy()
migrate = Migrate()

from app.i18n import i18n

def create_app():
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration - SQLite for local, PostgreSQL for production
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Production (Replit/PostgreSQL)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
            'pool_pre_ping': True,
            'pool_recycle': 300,
            'pool_size': 10,
            'max_overflow': 20
        }
    else:
        # Local development (SQLite)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devis_menuiserie.db'
        app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_AS_ASCII'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400
    
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    
    # Initialize i18n
    i18n.init_app(app)
    
    from app.routes import auth, catalog, quotes, users, settings, super_admin, email, languages
    
    app.register_blueprint(auth.bp)
    app.register_blueprint(catalog.bp)
    app.register_blueprint(quotes.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(settings.bp)
    app.register_blueprint(super_admin.bp)
    app.register_blueprint(email.bp)
    app.register_blueprint(languages.bp)
    
    from flask import render_template
    
    @app.route('/')
    def index():
        return render_template('dashboard.html')
    
    @app.route('/dashboard.html')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/quote.html')
    def quote():
        return render_template('quote.html')
    
    @app.route('/login.html')
    def login():
        return render_template('login.html')
    
    @app.route('/settings.html')
    def settings_page():
        return render_template('settings.html')
    
    @app.route('/profile.html')
    def profile_page():
        return render_template('profile.html')
    
    @app.route('/super-admin.html')
    def super_admin_page():
        return render_template('super_admin.html')
    
    @app.route('/super-admin-profile.html')
    def super_admin_profile_page():
        return render_template('super_admin_profile.html')
    
    @app.route('/super-admin-app-settings.html')
    def super_admin_app_settings_page():
        return render_template('super_admin_app_settings.html')
    
    @app.route('/super-admin-activity-logs.html')
    def super_admin_activity_logs_page():
        return render_template('super_admin_activity_logs.html')
    
    @app.route('/sw.js')
    def service_worker():
        from flask import send_from_directory
        return send_from_directory('static', 'sw.js', mimetype='application/javascript')
    
    @app.after_request
    def add_header(response):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    
    return app
