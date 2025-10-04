from flask import Blueprint, request, jsonify, session
from app.models import Company, User, Quote, Settings, AppSettings, ActivityLog, ChassisType, ProfileSeries, GlazingType, Finish, Accessory
from app import db
from app.routes.auth import super_admin_required, login_required
from datetime import datetime
from werkzeug.security import generate_password_hash
from app.crypto_utils import encrypt_data, decrypt_data

def copy_catalog_to_company(company_id):
    """Copy template catalog (company_id=NULL) to a new company"""
    try:
        # Copy chassis types
        template_chassis = ChassisType.query.filter_by(company_id=None).all()
        for chassis in template_chassis:
            new_chassis = ChassisType(
                company_id=company_id,
                name=chassis.name,
                description=chassis.description,
                min_width=chassis.min_width,
                max_width=chassis.max_width,
                min_height=chassis.min_height,
                max_height=chassis.max_height
            )
            db.session.add(new_chassis)
        
        # Copy profile series
        template_profiles = ProfileSeries.query.filter_by(company_id=None).all()
        for profile in template_profiles:
            new_profile = ProfileSeries(
                company_id=company_id,
                name=profile.name,
                description=profile.description,
                price_per_meter=profile.price_per_meter
            )
            db.session.add(new_profile)
        
        # Copy glazing types
        template_glazing = GlazingType.query.filter_by(company_id=None).all()
        for glazing in template_glazing:
            new_glazing = GlazingType(
                company_id=company_id,
                name=glazing.name,
                description=glazing.description,
                thickness_mm=glazing.thickness_mm,
                price_per_m2=glazing.price_per_m2
            )
            db.session.add(new_glazing)
        
        # Copy finishes
        template_finishes = Finish.query.filter_by(company_id=None).all()
        for finish in template_finishes:
            new_finish = Finish(
                company_id=company_id,
                name=finish.name,
                description=finish.description,
                price_coefficient=finish.price_coefficient
            )
            db.session.add(new_finish)
        
        # Copy accessories
        template_accessories = Accessory.query.filter_by(company_id=None).all()
        for accessory in template_accessories:
            new_accessory = Accessory(
                company_id=company_id,
                name=accessory.name,
                unit_price=accessory.unit_price,
                incompatible_series=accessory.incompatible_series
            )
            db.session.add(new_accessory)
        
        return True
    except Exception as e:
        print(f"Error copying catalog: {e}")
        return False

def log_activity(action, description=None):
    try:
        user_id = session.get('user_id')
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')
        
        log = ActivityLog(
            user_id=user_id,
            action=action,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")

bp = Blueprint('super_admin', __name__, url_prefix='/api/super-admin')

@bp.route('/companies', methods=['GET'])
@super_admin_required
def get_companies():
    companies = Company.query.order_by(Company.created_at.desc()).all()
    
    companies_data = []
    for company in companies:
        company_dict = company.to_dict()
        
        admin_count = User.query.filter_by(company_id=company.id, role='admin').count()
        user_count = User.query.filter_by(company_id=company.id, role='user').count()
        quote_count = Quote.query.filter_by(company_id=company.id).count()
        
        company_dict['admin_count'] = admin_count
        company_dict['user_count'] = user_count
        company_dict['quote_count'] = quote_count
        
        companies_data.append(company_dict)
    
    return jsonify(companies_data)

@bp.route('/companies/<int:company_id>/approve', methods=['POST'])
@super_admin_required
def approve_company(company_id):
    company = Company.query.get_or_404(company_id)
    
    if company.status == 'approved':
        return jsonify({'error': 'Company already approved'}), 400
    
    company.status = 'approved'
    company.approved_at = datetime.utcnow()
    company.approved_by = session['user_id']
    
    db.session.commit()
    
    log_activity('company_approved', f'Approved company: {company.name}')
    
    return jsonify({'success': True, 'company': company.to_dict()})

@bp.route('/companies/<int:company_id>/reject', methods=['POST'])
@super_admin_required
def reject_company(company_id):
    company = Company.query.get_or_404(company_id)
    
    company.status = 'rejected'
    
    db.session.commit()
    
    return jsonify({'success': True, 'company': company.to_dict()})

@bp.route('/companies/<int:company_id>/activate', methods=['POST'])
@super_admin_required
def activate_company(company_id):
    company = Company.query.get_or_404(company_id)
    
    company.status = 'approved'
    
    for user in company.users:
        user.is_active = True
    
    db.session.commit()
    
    return jsonify({'success': True, 'company': company.to_dict()})

@bp.route('/companies/<int:company_id>/deactivate', methods=['POST'])
@super_admin_required
def deactivate_company(company_id):
    company = Company.query.get_or_404(company_id)
    
    company.status = 'suspended'
    
    for user in company.users:
        user.is_active = False
    
    db.session.commit()
    
    return jsonify({'success': True, 'company': company.to_dict()})

@bp.route('/stats', methods=['GET'])
@super_admin_required
def get_stats():
    from datetime import datetime, timedelta
    
    total_companies = Company.query.count()
    active_companies = Company.query.filter_by(status='approved').count()
    pending_companies = Company.query.filter_by(status='pending').count()
    suspended_companies = Company.query.filter_by(status='suspended').count()
    
    total_users = User.query.filter(User.role != 'super_admin').count()
    total_admins = User.query.filter_by(role='admin').count()
    
    total_quotes = Quote.query.count()
    total_amount = db.session.query(db.func.sum(Quote.price_ttc)).scalar() or 0
    
    now = datetime.now()
    current_month = now.strftime('%Y-%m')
    month_quotes = Quote.query.filter(Quote.quote_date.like(f'{current_month}%')).count()
    
    month_quotes_list = Quote.query.filter(Quote.quote_date.like(f'{current_month}%')).all()
    month_amount = sum(q.price_ttc for q in month_quotes_list)
    
    week_start = (now - timedelta(days=now.weekday())).strftime('%Y-%m-%d')
    week_quotes = Quote.query.filter(Quote.quote_date >= week_start).count()
    
    week_quotes_list = Quote.query.filter(Quote.quote_date >= week_start).all()
    week_amount = sum(q.price_ttc for q in week_quotes_list)
    
    avg_quote_amount = total_amount / total_quotes if total_quotes > 0 else 0
    
    return jsonify({
        'total_companies': total_companies,
        'active_companies': active_companies,
        'pending_companies': pending_companies,
        'suspended_companies': suspended_companies,
        'total_users': total_users,
        'total_admins': total_admins,
        'total_quotes': total_quotes,
        'total_amount': round(total_amount, 2),
        'month_quotes': month_quotes,
        'month_amount': round(month_amount, 2),
        'week_quotes': week_quotes,
        'week_amount': round(week_amount, 2),
        'avg_quote_amount': round(avg_quote_amount, 2)
    })

@bp.route('/companies/create', methods=['POST'])
@super_admin_required
def create_company_with_admin():
    data = request.get_json()
    
    company_name = data.get('company_name')
    company_address = data.get('company_address', '')
    company_phone = data.get('company_phone', '')
    company_email = data.get('company_email', '')
    company_ice = data.get('company_ice', '')
    
    admin_username = data.get('admin_username')
    admin_full_name = data.get('admin_full_name')
    admin_email = data.get('admin_email')
    admin_password = data.get('admin_password')
    
    if not all([company_name, admin_username, admin_full_name, admin_email, admin_password]):
        return jsonify({'error': 'Required fields missing'}), 400
    
    if User.query.filter_by(username=admin_username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    try:
        current_user_id = session.get('user_id')
        
        company = Company()
        company.name = company_name
        company.status = 'approved'
        company.approved_by = current_user_id
        db.session.add(company)
        db.session.flush()
        
        settings = Settings()
        settings.company_id = company.id
        settings.company_name = company_name
        settings.address = encrypt_data(company_address) if company_address else None
        settings.phone = encrypt_data(company_phone) if company_phone else None
        settings.email = encrypt_data(company_email) if company_email else None
        settings.ice = encrypt_data(company_ice) if company_ice else None
        db.session.add(settings)
        
        admin = User()
        admin.username = admin_username
        admin.full_name = admin_full_name
        admin.email = admin_email
        admin.set_password(admin_password)
        admin.role = 'admin'
        admin.company_id = company.id
        admin.is_active = True
        db.session.add(admin)
        
        # Copy template catalog to the new company
        if not copy_catalog_to_company(company.id):
            raise Exception("Failed to copy catalog template")
        
        db.session.commit()
        
        log_activity('company_created', f'Created company: {company_name} with admin: {admin_username}')
        
        return jsonify({'success': True, 'message': 'Company and admin created successfully'})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/profile', methods=['GET'])
@super_admin_required
def get_profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'username': user.username,
        'full_name': user.full_name,
        'email': getattr(user, 'email', ''),
        'role': user.role
    })

@bp.route('/profile', methods=['PUT'])
@super_admin_required
def update_profile():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if 'full_name' in data:
        user.full_name = data['full_name']
    
    if 'email' in data and hasattr(user, 'email'):
        user.email = data['email']
    
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    db.session.commit()
    
    log_activity('profile_updated', 'Updated own profile')
    
    return jsonify({'success': True, 'message': 'Profile updated successfully'})

@bp.route('/app-settings', methods=['GET'])
@super_admin_required
def get_app_settings():
    settings = AppSettings.query.all()
    return jsonify([s.to_dict() for s in settings])

@bp.route('/app-settings', methods=['PUT'])
@super_admin_required
def update_app_settings():
    data = request.get_json()
    
    for key, value in data.items():
        setting = AppSettings.query.filter_by(key=key).first()
        if setting:
            setting.value = value
        else:
            setting = AppSettings(key=key, value=value)
            db.session.add(setting)
    
    db.session.commit()
    
    log_activity('app_settings_updated', f'Updated app settings: {", ".join(data.keys())}')
    
    return jsonify({'success': True, 'message': 'Settings updated successfully'})

@bp.route('/activity-logs', methods=['GET'])
@super_admin_required
def get_activity_logs():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'logs': [log.to_dict() for log in logs.items],
        'total': logs.total,
        'pages': logs.pages,
        'current_page': page
    })
