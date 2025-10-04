from flask import Blueprint, jsonify, request, session
from app.models import ChassisType, ProfileSeries, GlazingType, Finish, Accessory, Config
from app.routes.auth import login_required, admin_required
from app import db

bp = Blueprint('catalog', __name__, url_prefix='/api/catalog')

@bp.route('/chassis-types', methods=['GET'])
def get_chassis_types():
    company_id = session.get('company_id')
    chassis_types = ChassisType.query.filter_by(company_id=company_id).all()
    return jsonify([ct.to_dict() for ct in chassis_types])

@bp.route('/profile-series', methods=['GET'])
def get_profile_series():
    company_id = session.get('company_id')
    series = ProfileSeries.query.filter_by(company_id=company_id).all()
    return jsonify([s.to_dict() for s in series])

@bp.route('/glazing-types', methods=['GET'])
def get_glazing_types():
    company_id = session.get('company_id')
    glazing = GlazingType.query.filter_by(company_id=company_id).all()
    return jsonify([g.to_dict() for g in glazing])

@bp.route('/finishes', methods=['GET'])
def get_finishes():
    company_id = session.get('company_id')
    finishes = Finish.query.filter_by(company_id=company_id).all()
    return jsonify([f.to_dict() for f in finishes])

@bp.route('/accessories', methods=['GET'])
def get_accessories():
    company_id = session.get('company_id')
    accessories = Accessory.query.filter_by(company_id=company_id).all()
    return jsonify([a.to_dict() for a in accessories])

@bp.route('/config', methods=['GET'])
def get_config():
    configs = Config.query.all()
    return jsonify({c.key: float(c.value) for c in configs})

@bp.route('/chassis-types', methods=['POST'])
@admin_required
def create_chassis_type():
    data = request.json
    data['company_id'] = session.get('company_id')
    chassis = ChassisType(**data)
    db.session.add(chassis)
    db.session.commit()
    return jsonify(chassis.to_dict()), 201

@bp.route('/chassis-types/<int:id>', methods=['PUT'])
@admin_required
def update_chassis_type(id):
    company_id = session.get('company_id')
    chassis = ChassisType.query.filter_by(id=id, company_id=company_id).first_or_404()
    data = request.json
    for key, value in data.items():
        if key != 'company_id':
            setattr(chassis, key, value)
    db.session.commit()
    return jsonify(chassis.to_dict())

@bp.route('/chassis-types/<int:id>', methods=['DELETE'])
@admin_required
def delete_chassis_type(id):
    company_id = session.get('company_id')
    chassis = ChassisType.query.filter_by(id=id, company_id=company_id).first_or_404()
    db.session.delete(chassis)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/profile-series', methods=['POST'])
@admin_required
def create_profile_series():
    data = request.json
    data['company_id'] = session.get('company_id')
    series = ProfileSeries(**data)
    db.session.add(series)
    db.session.commit()
    return jsonify(series.to_dict()), 201

@bp.route('/profile-series/<int:id>', methods=['PUT'])
@admin_required
def update_profile_series(id):
    company_id = session.get('company_id')
    series = ProfileSeries.query.filter_by(id=id, company_id=company_id).first_or_404()
    data = request.json
    for key, value in data.items():
        if key != 'company_id':
            setattr(series, key, value)
    db.session.commit()
    return jsonify(series.to_dict())

@bp.route('/profile-series/<int:id>', methods=['DELETE'])
@admin_required
def delete_profile_series(id):
    company_id = session.get('company_id')
    series = ProfileSeries.query.filter_by(id=id, company_id=company_id).first_or_404()
    db.session.delete(series)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/glazing-types', methods=['POST'])
@admin_required
def create_glazing_type():
    data = request.json
    data['company_id'] = session.get('company_id')
    glazing = GlazingType(**data)
    db.session.add(glazing)
    db.session.commit()
    return jsonify(glazing.to_dict()), 201

@bp.route('/glazing-types/<int:id>', methods=['PUT'])
@admin_required
def update_glazing_type(id):
    company_id = session.get('company_id')
    glazing = GlazingType.query.filter_by(id=id, company_id=company_id).first_or_404()
    data = request.json
    for key, value in data.items():
        if key != 'company_id':
            setattr(glazing, key, value)
    db.session.commit()
    return jsonify(glazing.to_dict())

@bp.route('/glazing-types/<int:id>', methods=['DELETE'])
@admin_required
def delete_glazing_type(id):
    company_id = session.get('company_id')
    glazing = GlazingType.query.filter_by(id=id, company_id=company_id).first_or_404()
    db.session.delete(glazing)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/finishes', methods=['POST'])
@admin_required
def create_finish():
    data = request.json
    data['company_id'] = session.get('company_id')
    finish = Finish(**data)
    db.session.add(finish)
    db.session.commit()
    return jsonify(finish.to_dict()), 201

@bp.route('/finishes/<int:id>', methods=['PUT'])
@admin_required
def update_finish(id):
    company_id = session.get('company_id')
    finish = Finish.query.filter_by(id=id, company_id=company_id).first_or_404()
    data = request.json
    for key, value in data.items():
        if key != 'company_id':
            setattr(finish, key, value)
    db.session.commit()
    return jsonify(finish.to_dict())

@bp.route('/finishes/<int:id>', methods=['DELETE'])
@admin_required
def delete_finish(id):
    company_id = session.get('company_id')
    finish = Finish.query.filter_by(id=id, company_id=company_id).first_or_404()
    db.session.delete(finish)
    db.session.commit()
    return jsonify({'success': True})

@bp.route('/accessories', methods=['POST'])
@admin_required
def create_accessory():
    data = request.json
    data['company_id'] = session.get('company_id')
    accessory = Accessory(**data)
    db.session.add(accessory)
    db.session.commit()
    return jsonify(accessory.to_dict()), 201

@bp.route('/accessories/<int:id>', methods=['PUT'])
@admin_required
def update_accessory(id):
    company_id = session.get('company_id')
    accessory = Accessory.query.filter_by(id=id, company_id=company_id).first_or_404()
    data = request.json
    for key, value in data.items():
        if key != 'company_id':
            setattr(accessory, key, value)
    db.session.commit()
    return jsonify(accessory.to_dict())

@bp.route('/accessories/<int:id>', methods=['DELETE'])
@admin_required
def delete_accessory(id):
    company_id = session.get('company_id')
    accessory = Accessory.query.filter_by(id=id, company_id=company_id).first_or_404()
    db.session.delete(accessory)
    db.session.commit()
    return jsonify({'success': True})
