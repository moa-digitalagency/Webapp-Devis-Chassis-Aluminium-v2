from app import create_app, db
from app.models import User, Company, AppSettings
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
