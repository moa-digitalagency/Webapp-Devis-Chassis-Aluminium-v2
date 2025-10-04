from flask import Blueprint, request, jsonify
from app.models import Setting
from app.routes.auth import login_required, admin_required
from app import db

bp = Blueprint('settings', __name__, url_prefix='/api/settings')

@bp.route('', methods=['GET'])
@login_required
def get_settings():
    from flask import session
    section = request.args.get('section')
    company_id = session.get('company_id')
    
    if section:
        settings = Setting.query.filter_by(section=section, company_id=company_id).all()
    else:
        settings = Setting.query.filter_by(company_id=company_id).all()
    
    return jsonify([s.to_dict() for s in settings])

@bp.route('', methods=['POST'])
@admin_required
def update_settings():
    from flask import session
    data = request.json
    section = data.get('section')
    settings_data = data.get('settings', {})
    company_id = session.get('company_id')
    
    if not section:
        return jsonify({'error': 'Section required'}), 400
    
    for key, value in settings_data.items():
        setting = Setting.query.filter_by(section=section, key=key, company_id=company_id).first()
        if setting:
            setting.value = value
        else:
            setting = Setting(section=section, key=key, value=value, company_id=company_id)
            db.session.add(setting)
    
    db.session.commit()
    
    return jsonify({'success': True})
