from flask import Blueprint, jsonify, request, session
import os
import tempfile
from app.i18n import i18n
from app.routes.auth import login_required

bp = Blueprint('languages', __name__, url_prefix='/api/languages')

@bp.route('/available', methods=['GET'])
def get_available_languages():
    """Get list of available languages"""
    return jsonify(i18n.get_available_languages())

@bp.route('/current', methods=['GET'])
def get_current_language():
    """Get current language"""
    lang_code = i18n.get_current_language()
    return jsonify({
        'code': lang_code,
        'translations': i18n.get_translations(lang_code)
    })

@bp.route('/set', methods=['POST'])
def set_language():
    """Set current language"""
    data = request.get_json()
    lang_code = data.get('language')
    
    if not lang_code:
        return jsonify({'error': 'Language code required'}), 400
    
    if i18n.set_language(lang_code):
        return jsonify({
            'message': 'Language updated successfully',
            'code': lang_code
        })
    else:
        return jsonify({'error': 'Language not found'}), 404

@bp.route('/upload', methods=['POST'])
@login_required
def upload_language():
    """Upload a new language JSON file"""
    # Check if user is admin or super_admin
    role = session.get('role')
    if role not in ['admin', 'super_admin']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '' or file.filename is None:
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename or not file.filename.endswith('.json'):
        return jsonify({'error': 'File must be a JSON file'}), 400
    
    try:
        # Save to temporary file
        temp_fd, temp_path = tempfile.mkstemp(suffix='.json')
        os.close(temp_fd)
        file.save(temp_path)
        
        # Add language
        success, message = i18n.add_language(temp_path)
        
        # Clean up temp file
        os.unlink(temp_path)
        
        if success:
            return jsonify({
                'message': message,
                'languages': i18n.get_available_languages()
            })
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/translations/<lang_code>', methods=['GET'])
def get_translations(lang_code):
    """Get translations for a specific language"""
    translations = i18n.get_translations(lang_code)
    if translations:
        return jsonify(translations)
    else:
        return jsonify({'error': 'Language not found'}), 404
