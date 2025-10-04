from app import create_app, db
from app.models import (
    ChassisType, ProfileSeries, GlazingType, Finish, 
    Accessory, Pricing, Config, User
)

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()
    
    chassis_types_data = [
        {"name": "Baie vitrée coulissante", "description": "Grande ouverture coulissante", "min_width": 1000, "max_width": 5000, "min_height": 1000, "max_height": 3000},
        {"name": "Châssis fixe", "description": "Vitrage fixe sans ouverture", "min_width": 300, "max_width": 3000, "min_height": 300, "max_height": 2500},
        {"name": "Fenêtre 1/2 vantaux", "description": "Fenêtre à un ou deux vantaux", "min_width": 500, "max_width": 1800, "min_height": 500, "max_height": 1500},
        {"name": "Fenêtre oscillo-battant", "description": "Ouverture en soufflet et battante", "min_width": 500, "max_width": 1200, "min_height": 600, "max_height": 1800},
        {"name": "Porte avec imposte", "description": "Porte avec partie vitrée supérieure", "min_width": 800, "max_width": 1200, "min_height": 2000, "max_height": 2800},
        {"name": "Porte double", "description": "Deux vantaux", "min_width": 1400, "max_width": 2400, "min_height": 2000, "max_height": 2800},
        {"name": "Porte simple", "description": "Un vantail", "min_width": 700, "max_width": 1200, "min_height": 2000, "max_height": 2800}
    ]
    
    for data in chassis_types_data:
        chassis = ChassisType(**data)
        db.session.add(chassis)
    
    series_data = [
        {"name": "Série Fine", "description": "Profilé élégant pour utilisation standard", "price_per_meter": 35.00},
        {"name": "Série Renforcée", "description": "Profilé renforcé pour grandes dimensions", "price_per_meter": 45.00},
        {"name": "Série Thermique", "description": "Profilé à rupture de pont thermique, isolation optimale", "price_per_meter": 55.00}
    ]
    
    for data in series_data:
        series = ProfileSeries(**data)
        db.session.add(series)
    
    glazing_data = [
        {"name": "10mm - Simple", "description": "Simple vitrage 10mm", "thickness_mm": 10, "price_per_m2": 85.00},
        {"name": "4mm - Simple", "description": "Simple vitrage 4mm", "thickness_mm": 4, "price_per_m2": 45.00},
        {"name": "6mm - Simple", "description": "Simple vitrage 6mm", "thickness_mm": 6, "price_per_m2": 55.00},
        {"name": "4/6/4 - Double", "description": "Double vitrage 4/6/4", "thickness_mm": 14, "price_per_m2": 95.00},
        {"name": "6/8/6 - Double", "description": "Double vitrage 6/8/6", "thickness_mm": 20, "price_per_m2": 115.00},
        {"name": "8mm - Simple", "description": "Simple vitrage 8mm", "thickness_mm": 8, "price_per_m2": 70.00},
        {"name": "Feuilleté 4mm - Sécurité", "description": "Vitrage feuilleté sécurité", "thickness_mm": 8, "price_per_m2": 85.00},
        {"name": "Sécurité 6mm - Dépoli", "description": "Vitrage sécurité dépoli", "thickness_mm": 6, "price_per_m2": 120.00}
    ]
    
    for data in glazing_data:
        glazing = GlazingType(**data)
        db.session.add(glazing)
    
    finishes_data = [
        {"name": "Anodisé bronze", "description": "Finition anodisée bronze", "price_coefficient": 1.25},
        {"name": "Anodisé naturel", "description": "Finition anodisée naturelle", "price_coefficient": 1.20},
        {"name": "Aluminium brut", "description": "Aluminium brut standard", "price_coefficient": 1.0},
        {"name": "Imitation bois chêne", "description": "Aspect bois chêne", "price_coefficient": 1.50},
        {"name": "Imitation bois noyer", "description": "Aspect bois noyer", "price_coefficient": 1.50},
        {"name": "Thermolaqué noir", "description": "Peinture thermolaquée noir", "price_coefficient": 1.30}
    ]
    
    for data in finishes_data:
        finish = Finish(**data)
        db.session.add(finish)
    
    accessories_data = [
        {"name": "Charnière invisible (unité)", "unit_price": 18.00, "incompatible_series": None},
        {"name": "Charnière standard (unité)", "unit_price": 12.00, "incompatible_series": None},
        {"name": "Crémone renforcée", "unit_price": 55.00, "incompatible_series": None},
        {"name": "Crémone standard", "unit_price": 35.00, "incompatible_series": None}
    ]
    
    for data in accessories_data:
        acc = Accessory(**data)
        db.session.add(acc)
    
    pricing_data = [
        {"category": "labor", "subcategory": None, "unit": "unit", "price": 80.00, "coefficient": 1.0}
    ]
    
    for data in pricing_data:
        pricing = Pricing(**data)
        db.session.add(pricing)
    
    config_data = [
        {"key": "vat_rate", "value": "20"},
        {"key": "loss_coefficient", "value": "1.1"}
    ]
    
    for data in config_data:
        config = Config(**data)
        db.session.add(config)
    
    admin = User(username='admin', full_name='Administrateur', role='admin')
    admin.set_password('admin123')
    db.session.add(admin)
    
    db.session.commit()
    
    print("✅ Database seeded successfully with PostgreSQL!")
    print("👤 Admin user: admin / admin123")
