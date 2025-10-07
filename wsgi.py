"""
WSGI Configuration for Flask Application
This file is used by WSGI servers (Gunicorn, uWSGI, Apache mod_wsgi, etc.)
to serve the application in production environments.
"""
import os
import sys
from pathlib import Path

project_home = Path(__file__).parent.resolve()
if str(project_home) not in sys.path:
    sys.path.insert(0, str(project_home))

from app import create_app, db
from app.models import User, AppSettings
from dotenv import load_dotenv

load_dotenv()

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

if __name__ == "__main__":
    application.run()
