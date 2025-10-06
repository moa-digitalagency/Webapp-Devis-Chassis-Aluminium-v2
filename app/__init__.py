from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os
import secrets
from cryptography.fernet import Fernet

db = SQLAlchemy()
migrate = Migrate()

from app.i18n import i18n

def create_app():
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    secret_key = os.environ.get('SECRET_KEY')
    if not secret_key:
        secret_key = secrets.token_hex(32)
        print("\n" + "="*60)
        print("⚠️  WARNING: SECRET_KEY not found in environment!")
        print("Generated temporary key for this session.")
        print("Generate and add yours with:")
        print("  python -c \"import secrets; print('SECRET_KEY=' + secrets.token_hex(32))\"")
        print("="*60 + "\n")
    
    app.config['SECRET_KEY'] = secret_key
    
    encryption_key = os.environ.get('ENCRYPTION_KEY')
    if not encryption_key:
        encryption_key = Fernet.generate_key().decode()
        print("\n" + "="*60)
        print("⚠️  WARNING: ENCRYPTION_KEY not found in environment!")
        print("Generated temporary key for this session.")
        print("Generate and add yours with:")
        print("  python -c \"from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())\"")
        print("="*60 + "\n")
    else:
        try:
            test_cipher = Fernet(encryption_key.encode())
            test_cipher.encrypt(b'test')
        except Exception as e:
            print("\n" + "="*60)
            print("❌ ERROR: ENCRYPTION_KEY is invalid!")
            print(f"Error: {e}")
            print("Generate a valid key with:")
            print("  python -c \"from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())\"")
            print("="*60 + "\n")
            encryption_key = Fernet.generate_key().decode()
            print(f"⚠️  Using temporary key for this session: {encryption_key}")
    
    os.environ['ENCRYPTION_KEY'] = encryption_key
    
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
    
    is_production = database_url is not None
    
    if is_production:
        app.config['SESSION_COOKIE_SAMESITE'] = 'None'
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_HTTPONLY'] = True
    else:
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        app.config['SESSION_COOKIE_SECURE'] = False
    
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    if is_production:
        railway_domain = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
        pythonanywhere_domain = os.environ.get('PYTHONANYWHERE_DOMAIN')
        allowed_origins_env = os.environ.get('ALLOWED_ORIGINS', '')
        
        if railway_domain and not allowed_origins_env:
            allowed_origins = [f'https://{railway_domain}']
            print(f"\n✅ CORS: Auto-detected Railway domain: {railway_domain}")
        elif pythonanywhere_domain and not allowed_origins_env:
            allowed_origins = [f'https://{pythonanywhere_domain}']
            print(f"\n✅ CORS: Auto-detected PythonAnywhere domain: {pythonanywhere_domain}")
        elif allowed_origins_env:
            allowed_origins = [origin.strip() for origin in allowed_origins_env.split(',')]
        else:
            allowed_origins = None
            print("\n" + "="*60)
            print("⚠️  WARNING: No specific domain detected for CORS")
            print("Using permissive CORS with credentials support")
            print("For better security, set one of:")
            print("  ALLOWED_ORIGINS=https://your-app.up.railway.app")
            print("  RAILWAY_PUBLIC_DOMAIN=your-app.up.railway.app")
            print("  PYTHONANYWHERE_DOMAIN=yourusername.pythonanywhere.com")
            print("="*60 + "\n")
        
        if allowed_origins:
            CORS(app, 
                 supports_credentials=True,
                 origins=allowed_origins,
                 allow_headers=['Content-Type', 'Authorization'],
                 methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
        else:
            CORS(app,
                 supports_credentials=True,
                 origins='*',
                 allow_headers=['Content-Type', 'Authorization'],
                 methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
            
            @app.after_request
            def cors_credentials_fix(response):
                origin = request.headers.get('Origin')
                if origin:
                    response.headers['Access-Control-Allow-Origin'] = origin
                    response.headers['Access-Control-Allow-Credentials'] = 'true'
                return response
    else:
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
