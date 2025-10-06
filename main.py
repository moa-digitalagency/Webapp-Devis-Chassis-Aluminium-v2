from app import create_app, db
from app.models import User, Company, AppSettings
import os
import secrets
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def ensure_secrets():
    """Ensure SECRET_KEY and ENCRYPTION_KEY exist, generate if needed."""
    env_file = '.env'
    secret_key = os.environ.get('SECRET_KEY')
    encryption_key = os.environ.get('ENCRYPTION_KEY')
    
    needs_update = False
    env_lines = []
    
    # Read existing .env file if it exists
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            env_lines = f.readlines()
    
    # Check and generate SECRET_KEY if needed
    if not secret_key:
        secret_key = secrets.token_hex(32)
        os.environ['SECRET_KEY'] = secret_key
        needs_update = True
        print("✅ Generated new SECRET_KEY")
    
    # Check and generate ENCRYPTION_KEY if needed
    if not encryption_key:
        encryption_key = Fernet.generate_key().decode()
        os.environ['ENCRYPTION_KEY'] = encryption_key
        needs_update = True
        print("✅ Generated new ENCRYPTION_KEY")
    
    # Update .env file if new keys were generated
    if needs_update:
        # Remove old SECRET_KEY and ENCRYPTION_KEY lines if they exist
        env_lines = [line for line in env_lines if not line.startswith('SECRET_KEY=') and not line.startswith('ENCRYPTION_KEY=')]
        
        # Add new keys
        if not any(line.startswith('SECRET_KEY=') for line in env_lines):
            env_lines.append(f'SECRET_KEY={secret_key}\n')
        if not any(line.startswith('ENCRYPTION_KEY=') for line in env_lines):
            env_lines.append(f'ENCRYPTION_KEY={encryption_key}\n')
        
        # Write to .env file
        with open(env_file, 'w') as f:
            f.writelines(env_lines)
        
        print(f"💾 Keys saved to {env_file}")
        print("⚠️  IMPORTANT: Keep this file secure and backed up!")
        print("⚠️  If you lose ENCRYPTION_KEY, encrypted data will be unrecoverable!\n")

# Ensure secrets exist before creating app
ensure_secrets()

app = create_app()

def init_database():
    """Initialize the database with default data."""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created")
        
        # Create default super admin if doesn't exist
        if not User.query.filter_by(username='superadmin').first():
            superadmin = User(
                username='superadmin',
                full_name='Super Administrateur',
                email='admin@example.com',
                role='super_admin',
                company_id=None
            )
            superadmin.set_password('admin123')
            db.session.add(superadmin)
            db.session.commit()
            print("✓ Super admin created (username: superadmin, password: admin123)")
        
        # Create default app settings if they don't exist
        if not AppSettings.query.first():
            default_settings = [
                AppSettings(key='app_name', value='PWA Devis Menuiserie'),
                AppSettings(key='app_version', value='1.0.0'),
                AppSettings(key='app_title', value='Devis Châssis Aluminium'),
                AppSettings(key='sendgrid_from_name', value='Devis Menuiserie')
            ]
            for setting in default_settings:
                db.session.add(setting)
            db.session.commit()
            print("✓ Default app settings created")
        
        print("\n=== Database initialized successfully! ===")
        print("You can now login with:")
        print("  Username: superadmin")
        print("  Password: admin123")
        print("\nAccess the application at: http://localhost:5000")

@app.cli.command()
def init_db():
    """Initialize the database (Flask CLI command)."""
    init_database()

if __name__ == '__main__':
    # Auto-initialize database on first run
    with app.app_context():
        try:
            # Check if database exists and has data
            if not User.query.first():
                print("\n=== First time setup - Initializing database ===\n")
                init_database()
        except Exception as e:
            # Database doesn't exist or tables not created
            print("\n=== Initializing database ===\n")
            init_database()
    
    print("\n=== Starting Flask development server ===\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
