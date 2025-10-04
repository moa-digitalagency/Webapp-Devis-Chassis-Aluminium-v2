from flask import Blueprint, request, jsonify, session
from app.models import User
from app import db
from functools import wraps

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        if session.get('role') not in ['admin', 'super_admin']:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        if session.get('role') != 'super_admin':
            return jsonify({'error': 'Super admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is not active'}), 403
    
    if user.role != 'super_admin' and user.company_id:
        from app.models import Company
        company = Company.query.get(user.company_id)
        if not company or company.status != 'approved':
            return jsonify({'error': 'Company is not approved'}), 403
    
    session.permanent = True
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    session['full_name'] = user.full_name
    session['company_id'] = user.company_id
    
    return jsonify({
        'success': True,
        'user': user.to_dict()
    })

@bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@bp.route('/check', methods=['GET'])
def check():
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'user': {
                'id': session.get('user_id'),
                'username': session.get('username'),
                'role': session.get('role'),
                'full_name': session.get('full_name'),
                'company_id': session.get('company_id')
            }
        })
    return jsonify({'authenticated': False})
