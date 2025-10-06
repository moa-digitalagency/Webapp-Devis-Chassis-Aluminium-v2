# PWA Devis Menuiserie

## Overview
PWA Devis Menuiserie is a **multi-tenant SaaS Progressive Web App** for aluminum joinery salespersons. It generates quotes for chassis (windows, doors, bay windows) with automated pricing, PDF generation, offline capability, and **email delivery via SendGrid**. The app supports multiple companies with data isolation, role-based access, and a super admin dashboard for company management and approval workflows. It aims to streamline sales, provide accurate pricing, and ensure business continuity.

## User Preferences
I prefer iterative development with a focus on clear, modular code. Please prioritize robust error handling and security in all implementations. For any significant architectural changes or new feature implementations, I'd like to be consulted before they are applied. I appreciate detailed explanations for complex solutions. Do not make changes to the `docs/` folder.

## Recent Changes

### October 6, 2025 - Critical Multi-Platform Deployment Fix
- **FIXED**: "Server connection error" on login across all deployment platforms (Railway, Python Anywhere, Render)
- **Root cause**: CORS configuration with `origins='*'` + `supports_credentials=False` caused browsers to reject session cookies
- **Solution**: Implemented intelligent CORS with origin reflection and credential support using `@app.after_request`
- **Auto-detection**: Added support for `RAILWAY_PUBLIC_DOMAIN` and `PYTHONANYWHERE_DOMAIN` environment variables
- **Fallback**: Permissive CORS with credentials enabled when no specific domain is configured
- **Frontend**: All fetch() calls now include `credentials: 'include'` for proper session handling
- **Production cookies**: Properly configured with `SameSite=None` and `Secure=True` for HTTPS
- **Updated**: DEPLOY_RAILWAY.md renamed to comprehensive multi-platform deployment guide

## System Architecture
The application uses an Application Factory pattern with Flask and modular blueprints. It has a mobile-first, responsive frontend.

-   **Backend**: Python Flask with SQLAlchemy ORM. **Database support**: SQLite (local development, default) or PostgreSQL (production). Features a RESTful API, server-side validation, multi-item quote support, PDF generation with ReportLab, CSV import for tariff updates, **SendGrid email integration**, and a robust authentication system with roles (admin/user/super_admin). It implements a **multi-tenant SaaS architecture** with `company_id` for data isolation and a centralized `settings` table for company-specific configurations.
    -   **Auto-initialization**: On first run, the database is automatically initialized with tables and a default super admin (username: `superadmin`, password: `admin123`).
-   **Frontend**: Modern login page and admin dashboards. HTML/CSS/JS provides a guided 8-step quote creation interface with real-time validation and instant price calculation using MAD (Dirham). Supports multi-item quotes with add/edit/delete capabilities. A **hamburger sidebar menu** on admin pages provides access to profile, settings, and other features.
    -   **Quote Creation Steps**: Product selection, dimensions (with real-time surface calculation), profile series, glazing types, accessories, finishes, client information, and a multi-item summary with total, edit/delete options, and a "Send by Email" button.
-   **UI/UX**: Modern design with rounded borders, a subtle diagonal crosshatch background pattern (2% opacity) on admin pages, a split-screen login page with a gradient background, emoji-enhanced titles, and standardized button styles. Prices are displayed in a blue theme color, and currency is formatted as `1.234,56 MAD`.
-   **Performance**: Targets sub-0.5s price calculation and sub-2s PDF generation (<500KB).
-   **Security**: PBKDF2-SHA256 for password hashing, Fernet encryption (AES-128) for sensitive data, server-side validation, role-based access control with company-level data isolation, activity logging, and SendGrid API key managed via Replit Connector.
-   **Email Integration**: Utilizes a **SendGrid connector** via Replit for sending beautifully formatted HTML emails with quote details. API endpoints include `/api/email/send-quote` and `/api/email/test-connection`. Configurable "From Name" via super admin settings.
-   **SaaS Multi-Tenancy**:
    -   **Company Model**: Central `companies` table with approval workflow.
    -   **Data Isolation**: All business data (quotes, settings, users, catalog items) are isolated by `company_id`.
    -   **Catalog Multi-Tenancy**: Catalog tables include `company_id`. A template catalog is copied to new companies, allowing independent modification.
    -   **User Isolation**: Admins only see users from their own company.
    -   **Roles**: Three-tier system (user, admin, super_admin).
    -   **Super Admin Features**: Company management dashboard with approval capabilities, dedicated profile, app settings (including text customization for `app_title`, `sendgrid_from_name`, etc.), activity logs, and extended statistics. New companies are created via a 2-step wizard.
    -   **Authentication Flow**: Checks user and company status.
-   **Data Structure**: Accessories are stored as `{name: quantity}` objects. Multi-item quotes store configurations in a `breakdown.items` array. `User` table includes a mandatory `email` field.
-   **Offline Functionality**: All CSS/JS files are local, and a Service Worker provides full offline PWA functionality.
-   **CSS Build System**: Uses Tailwind CSS v4 standalone binary with pure CSS configuration. **100% Python stack - no Node.js or npm required**. Tailwind builds via `./tailwindcss` binary with CSS-based config in `tailwind-input.css`.
-   **Internationalization (i18n)**: Multi-language support via JSON translation files. Default languages: French (fr) and English (en). Super admins can upload new language files via the admin interface. Languages are stored in `app/locales/` and automatically scanned at startup. API endpoints: `/api/languages/available`, `/api/languages/current`, `/api/languages/set`, `/api/languages/upload`. Frontend includes a language switcher and translation system (`i18n.js`).
-   **Backup System**: Automated and manual database backup functionality for both SQLite and PostgreSQL. Features include:
    -   **Manual Backup**: Super admins can create backups on-demand via the dashboard
    -   **Auto Backup**: Automatic backup before system updates
    -   **Backup Catalog**: Tracks all backups with metadata (timestamp, size, description, status)
    -   **Restore Capability**: Restore from any successful backup
    -   **Storage Management**: Automatic cleanup (keeps last 10 backups by default)
    -   Service located in `app/services/backup.py`
    -   API endpoints: `/api/super-admin/backup/create`, `/api/super-admin/backup/list`, `/api/super-admin/backup/restore`
-   **GitHub Update System**: Automated application updates from GitHub repository with database migration support. Features include:
    -   **Update Detection**: Checks for available updates from https://github.com/moa-digitalagency/Webapp-Devis-Chassis-Aluminium-v2
    -   **Auto Migration**: Runs Flask-Migrate database migrations automatically
    -   **Dependency Update**: Automatically installs new requirements
    -   **Git Integration**: Pull updates from specified branch (default: main)
    -   **Update History**: Tracks all update attempts with detailed logs
    -   **Rollback Support**: Ability to rollback to previous commits
    -   **Pre-Update Backup**: Creates automatic backup before updating
    -   Service located in `app/services/updater.py`
    -   API endpoints: `/api/super-admin/update/check`, `/api/super-admin/update/perform`, `/api/super-admin/update/history`, `/api/super-admin/update/rollback`

## External Dependencies
-   **Database**: SQLite (default, local) or PostgreSQL (production, Replit).
-   **SQLAlchemy**: ORM for database interaction.
-   **Flask-Migrate**: For database schema migrations.
-   **ReportLab**: For PDF document generation.
-   **Requests**: HTTP library.
-   **SendGrid**: Email delivery service, integrated via Replit Connector.
-   **python-dotenv**: Environment variable management from `.env` file.

## Installation Support
-   **Windows**: Fully supported with winget-based installation (Python 3.11, Git, SQLite). Complete instructions in README.md.
-   **Linux/Mac**: Standard Python venv workflow with SQLite or PostgreSQL.
-   **Replit**: Native PostgreSQL database support with automatic configuration. The application is fully configured and ready to run on Replit with:
    -   PostgreSQL database (automatically connected via DATABASE_URL environment variable)
    -   All Python dependencies installed (Flask, SQLAlchemy, ReportLab, etc.)
    -   Flask workflow configured to run on port 5000
    -   Production deployment configured with Gunicorn for autoscaling
    -   Database auto-initialization on first run with default super admin credentials

## Replit Environment Setup (Completed)
-   **Database**: PostgreSQL database created and configured
-   **Python**: Python 3.11 with all required packages installed
-   **Workflow**: Flask App running on port 5000 (development mode)
-   **Deployment**: Configured for autoscale deployment with Gunicorn
-   **Default Credentials**: 
    -   Super Admin: `superadmin` / `admin123`
    -   Admin: `admin` / `admin123` (if created)