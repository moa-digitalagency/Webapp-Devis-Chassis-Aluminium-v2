from app import db
from datetime import datetime
from hashlib import pbkdf2_hmac
import secrets


class ChassisType(db.Model):
    __tablename__ = 'chassis_types'
    __table_args__ = (
        db.UniqueConstraint('company_id', 'name', name='uq_chassis_types_company_name'),
    )

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    min_width = db.Column(db.Integer, nullable=False)
    max_width = db.Column(db.Integer, nullable=False)
    min_height = db.Column(db.Integer, nullable=False)
    max_height = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'name': self.name,
            'description': self.description,
            'min_width': self.min_width,
            'max_width': self.max_width,
            'min_height': self.min_height,
            'max_height': self.max_height
        }


class ProfileSeries(db.Model):
    __tablename__ = 'profile_series'
    __table_args__ = (
        db.UniqueConstraint('company_id', 'name', name='uq_profile_series_company_name'),
    )

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price_per_meter = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'name': self.name,
            'description': self.description,
            'price_per_meter': self.price_per_meter
        }


class GlazingType(db.Model):
    __tablename__ = 'glazing_types'
    __table_args__ = (
        db.UniqueConstraint('company_id', 'name', name='uq_glazing_types_company_name'),
    )

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    thickness_mm = db.Column(db.Integer)
    price_per_m2 = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'name': self.name,
            'description': self.description,
            'thickness_mm': self.thickness_mm,
            'price_per_m2': self.price_per_m2
        }


class Finish(db.Model):
    __tablename__ = 'finishes'
    __table_args__ = (
        db.UniqueConstraint('company_id', 'name', name='uq_finishes_company_name'),
    )

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price_coefficient = db.Column(db.Float, nullable=False, default=1.0)

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'name': self.name,
            'description': self.description,
            'price_coefficient': self.price_coefficient
        }


class Accessory(db.Model):
    __tablename__ = 'accessories'
    __table_args__ = (
        db.UniqueConstraint('company_id', 'name', name='uq_accessories_company_name'),
    )

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    incompatible_series = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'name': self.name,
            'unit_price': self.unit_price,
            'incompatible_series': self.incompatible_series
        }


class Pricing(db.Model):
    __tablename__ = 'pricing'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(100), nullable=False)
    subcategory = db.Column(db.String(100))
    unit = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    coefficient = db.Column(db.Float, default=1.0)

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'subcategory': self.subcategory,
            'unit': self.unit,
            'price': self.price,
            'coefficient': self.coefficient
        }


class Quote(db.Model):
    __tablename__ = 'quotes'

    id = db.Column(db.Integer, primary_key=True)
    quote_number = db.Column(db.String(50), nullable=False, unique=True)
    quote_date = db.Column(db.String(20), nullable=False)
    chassis_type = db.Column(db.String(100), nullable=False)
    width = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Integer, nullable=False)
    profile_series = db.Column(db.String(100), nullable=False)
    glazing_type = db.Column(db.String(100), nullable=False)
    finish = db.Column(db.String(100), nullable=False)
    accessories = db.Column(db.Text)
    discount_percent = db.Column(db.Float, default=0)
    price_ht = db.Column(db.Float, nullable=False)
    price_ttc = db.Column(db.Float, nullable=False)
    details = db.Column(db.Text, nullable=False)
    company_id = db.Column(db.Integer,
                           db.ForeignKey('companies.id'),
                           nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'quote_number': self.quote_number,
            'quote_date': self.quote_date,
            'chassis_type': self.chassis_type,
            'width': self.width,
            'height': self.height,
            'profile_series': self.profile_series,
            'glazing_type': self.glazing_type,
            'finish': self.finish,
            'accessories': self.accessories,
            'discount_percent': self.discount_percent,
            'price_ht': self.price_ht,
            'price_ttc': self.price_ttc,
            'details': self.details,
            'company_id': self.company_id,
            'created_at':
            self.created_at.isoformat() if self.created_at else None
        }


class Config(db.Model):
    __tablename__ = 'config'

    key = db.Column(db.String(100), primary_key=True)
    value = db.Column(db.Text, nullable=False)

    def to_dict(self):
        return {'key': self.key, 'value': self.value}


class AuditLog(db.Model):
    __tablename__ = 'audit_log'

    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'action': self.action,
            'details': self.details,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    full_name = db.Column(db.String(200))
    email = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    company_id = db.Column(db.Integer,
                           db.ForeignKey('companies.id'),
                           nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        salt = secrets.token_bytes(32)
        self.password_hash = salt.hex() + pbkdf2_hmac(
            'sha256', password.encode(), salt, 100000).hex()

    def check_password(self, password):
        salt = bytes.fromhex(self.password_hash[:64])
        stored_hash = self.password_hash[64:]
        computed_hash = pbkdf2_hmac('sha256', password.encode(), salt,
                                    100000).hex()
        return computed_hash == stored_hash

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'full_name': self.full_name,
            'email': self.email,
            'role': self.role,
            'company_id': self.company_id,
            'is_active': self.is_active,
            'created_at':
            self.created_at.isoformat() if self.created_at else None
        }


class Setting(db.Model):
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(50), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Text)
    company_id = db.Column(db.Integer,
                           db.ForeignKey('companies.id'),
                           nullable=True)

    __table_args__ = (db.UniqueConstraint('section',
                                          'key',
                                          'company_id',
                                          name='_section_key_company_uc'), )

    def to_dict(self):
        return {
            'id': self.id,
            'section': self.section,
            'key': self.key,
            'value': self.value,
            'company_id': self.company_id
        }


class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    approved_by = db.Column(db.Integer,
                            db.ForeignKey('users.id'),
                            nullable=True)

    users = db.relationship('User',
                            foreign_keys='User.company_id',
                            backref='company',
                            lazy=True)
    quotes = db.relationship('Quote',
                             foreign_keys='Quote.company_id',
                             backref='company',
                             lazy=True)
    settings = db.relationship('Setting',
                               foreign_keys='Setting.company_id',
                               backref='company',
                               lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'created_at':
            self.created_at.isoformat() if self.created_at else None,
            'approved_at':
            self.approved_at.isoformat() if self.approved_at else None,
            'approved_by': self.approved_by
        }


class Settings(db.Model):
    __tablename__ = 'company_settings'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer,
                           db.ForeignKey('companies.id'),
                           nullable=False,
                           unique=True)
    company_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.Text)
    phone = db.Column(db.Text)
    email = db.Column(db.Text)
    ice = db.Column(db.Text)
    min_width = db.Column(db.Integer, default=300)
    max_width = db.Column(db.Integer, default=3000)
    min_height = db.Column(db.Integer, default=300)
    max_height = db.Column(db.Integer, default=3000)

    def to_dict(self):
        from app.crypto_utils import decrypt_data
        return {
            'id': self.id,
            'company_id': self.company_id,
            'company_name': self.company_name,
            'address': decrypt_data(self.address) if self.address else '',
            'phone': decrypt_data(self.phone) if self.phone else '',
            'email': decrypt_data(self.email) if self.email else '',
            'ice': decrypt_data(self.ice) if self.ice else '',
            'min_width': self.min_width or 300,
            'max_width': self.max_width or 3000,
            'min_height': self.min_height or 300,
            'max_height': self.max_height or 3000
        }


class AppSettings(db.Model):
    __tablename__ = 'app_settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False, unique=True)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime,
                           default=datetime.utcnow,
                           onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'updated_at':
            self.updated_at.isoformat() if self.updated_at else None
        }


class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'description': self.description,
            'ip_address': self.ip_address,
            'created_at':
            self.created_at.isoformat() if self.created_at else None
        }
