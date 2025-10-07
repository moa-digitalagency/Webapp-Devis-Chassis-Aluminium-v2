"""
PythonAnywhere WSGI Configuration
This file is specifically configured for PythonAnywhere hosting.
"""
import os
import sys
from pathlib import Path

project_home = '/home/yourusername/Webapp-Devis-Chassis-Aluminium-v2'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from dotenv import load_dotenv

project_folder = Path(__file__).parent.resolve()
load_dotenv(project_folder / '.env')

from app import create_app, db
from app.models import User, AppSettings

application = create_app()

def init_database():
    """Initialize the database with default data."""
    with application.app_context():
        db.create_all()
        
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

with application.app_context():
    try:
        if not User.query.first():
            init_database()
    except Exception:
        init_database()
