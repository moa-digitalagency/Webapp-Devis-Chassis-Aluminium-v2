from flask import Blueprint, request, jsonify, session
from app.models import User
from app.routes.auth import admin_required, login_required
from app import db

bp = Blueprint('users', __name__, url_prefix='/api/users')

@bp.route('', methods=['GET'])
@admin_required
def get_users():
    role = session.get('role')
    company_id = session.get('company_id')
    
    # Super admin sees all users
    if role == 'super_admin':
        users = User.query.all()
    # Company admin sees only users from their company (not super_admins)
    else:
        users = User.query.filter_by(company_id=company_id).filter(User.role != 'super_admin').all()
    
    return jsonify([user.to_dict() for user in users])

@bp.route('', methods=['POST'])
@admin_required
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    full_name = data.get('full_name', '')
    role = data.get('role', 'user')
    email = data.get('email', '')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    if not email:
        return jsonify({'error': 'Email is required'}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    # Get company_id from session (for company admins)
    company_id = session.get('company_id')
    
    user = User(
        username=username, 
        full_name=full_name, 
        role=role,
        email=email,
        company_id=company_id
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'success': True, 'user': user.to_dict()})

@bp.route('/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    if user_id == session.get('user_id'):
        return jsonify({'error': 'Cannot delete your own account'}), 400
    
    role = session.get('role')
    company_id = session.get('company_id')
    
    # Company admin can only delete users from their company
    if role != 'super_admin':
        user = User.query.filter_by(id=user_id, company_id=company_id).first_or_404()
    else:
        user = User.query.get_or_404(user_id)
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'User deleted'})

@bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@bp.route('/me', methods=['PUT'])
@login_required
def update_current_user():
    user_id = session.get('user_id')
    user = User.query.get_or_404(user_id)
    
    data = request.json
    full_name = data.get('full_name')
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if full_name:
        user.full_name = full_name
    
    if new_password:
        if not current_password:
            return jsonify({'error': 'Current password required'}), 400
        
        if not user.check_password(current_password):
            return jsonify({'error': 'Current password incorrect'}), 400
        
        user.set_password(new_password)
    
    db.session.commit()
    
    return jsonify({'success': True, 'user': user.to_dict()})
