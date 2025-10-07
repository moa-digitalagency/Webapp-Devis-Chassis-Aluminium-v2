from app import create_app, db
from app.models import (
    Company, User, ChassisType, ProfileSeries, 
    GlazingType, Finish, Accessory
)
from datetime import datetime

app = create_app()

with app.app_context():
    demo_company = Company.query.filter_by(name='Entreprise Demo').first()
    
    if demo_company:
        print("⚠️  L'entreprise demo existe déjà. Suppression...")
        User.query.filter_by(company_id=demo_company.id).delete()
        ChassisType.query.filter_by(company_id=demo_company.id).delete()
        ProfileSeries.query.filter_by(company_id=demo_company.id).delete()
        GlazingType.query.filter_by(company_id=demo_company.id).delete()
        Finish.query.filter_by(company_id=demo_company.id).delete()
        Accessory.query.filter_by(company_id=demo_company.id).delete()
        db.session.delete(demo_company)
        db.session.commit()
    
    print("\n" + "="*60)
    print("🏢 Création de l'entreprise demo...")
    print("="*60 + "\n")
    
    demo_company = Company(
        name='Entreprise Demo',
        status='approved',
        approved_at=datetime.utcnow()
    )
    db.session.add(demo_company)
    db.session.flush()
    
    company_id = demo_company.id
    
    print("✅ Entreprise créée: Entreprise Demo")
    
    admin_user = User(
        username='demo',
        full_name='Admin Demo',
        email='demo@example.com',
        role='admin',
        company_id=company_id
    )
    admin_user.set_password('demo123')
    db.session.add(admin_user)
    print("✅ Utilisateur admin créé: demo / demo123")
    
    print("\n📦 Ajout des types de châssis...")
    chassis_types_data = [
        {
            "name": "Baie vitrée coulissante",
            "description": "Baie vitrée coulissante en aluminium",
            "min_width": 100,
            "max_width": 5000,
            "min_height": 100,
            "max_height": 3000
        },
        {
            "name": "Châssis fixe",
            "description": "Châssis fixe / verrière",
            "min_width": 100,
            "max_width": 5000,
            "min_height": 100,
            "max_height": 3000
        },
        {
            "name": "Fenêtre 1 vantail",
            "description": "Fenêtre aluminium avec un seul vantail ouvrant",
            "min_width": 100,
            "max_width": 5000,
            "min_height": 100,
            "max_height": 3000
        },
        {
            "name": "Fenêtre 2 vantaux",
            "description": "Fenêtre aluminium avec deux vantaux ouvrants",
            "min_width": 100,
            "max_width": 5000,
            "min_height": 100,
            "max_height": 3000
        },
        {
            "name": "Fenêtre oscillo-battant",
            "description": "Fenêtre aluminium avec système oscillo-battant",
            "min_width": 100,
            "max_width": 5000,
            "min_height": 100,
            "max_height": 3000
        },
        {
            "name": "Porte avec imposte",
            "description": "Porte aluminium avec imposte vitrée",
            "min_width": 100,
            "max_width": 5000,
            "min_height": 100,
            "max_height": 3000
        },
        {
            "name": "Porte double",
            "description": "Porte aluminium à deux vantaux",
            "min_width": 100,
            "max_width": 5000,
            "min_height": 100,
            "max_height": 3000
        },
        {
            "name": "Porte simple",
            "description": "Porte aluminium simple",
            "min_width": 100,
            "max_width": 5000,
            "min_height": 100,
            "max_height": 3000
        }
    ]
    
    for data in chassis_types_data:
        chassis = ChassisType(company_id=company_id, **data)
        db.session.add(chassis)
        print(f"  ✓ {data['name']}")
    
    print("\n🔧 Ajout des séries de profilés...")
    series_data = [
        {
            "name": "Série Fine",
            "description": "Profilé élégant pour utilisation standard",
            "price_per_meter": 100.00
        },
        {
            "name": "Série Renforcée",
            "description": "Profilé renforcé pour grandes dimensions",
            "price_per_meter": 130.00
        },
        {
            "name": "Série Thermique",
            "description": "Profilé à rupture de pont thermique, isolation optimale",
            "price_per_meter": 150.00
        }
    ]
    
    for data in series_data:
        series = ProfileSeries(company_id=company_id, **data)
        db.session.add(series)
        print(f"  ✓ {data['name']}")
    
    print("\n🪟 Ajout des types de vitrage...")
    glazing_data = [
        {
            "name": "10mm",
            "description": "Simple",
            "thickness_mm": 10,
            "price_per_m2": 85.00
        },
        {
            "name": "4mm",
            "description": "Simple",
            "thickness_mm": 4,
            "price_per_m2": 45.00
        },
        {
            "name": "6mm",
            "description": "Simple",
            "thickness_mm": 6,
            "price_per_m2": 55.00
        },
        {
            "name": "8mm",
            "description": "Simple",
            "thickness_mm": 8,
            "price_per_m2": 70.00
        },
        {
            "name": "4/6/4",
            "description": "Double",
            "thickness_mm": 14,
            "price_per_m2": 95.00
        },
        {
            "name": "6/8/6",
            "description": "Double",
            "thickness_mm": 20,
            "price_per_m2": 115.00
        },
        {
            "name": "Feuilleté 4mm",
            "description": "Feuilleté",
            "thickness_mm": 4,
            "price_per_m2": 85.00
        },
        {
            "name": "Sécurité 6mm",
            "description": "Sécurité",
            "thickness_mm": 6,
            "price_per_m2": 120.00
        }
    ]
    
    for data in glazing_data:
        glazing = GlazingType(company_id=company_id, **data)
        db.session.add(glazing)
        print(f"  ✓ {data['name']} - {data['description']}")
    
    print("\n🎨 Ajout des finitions...")
    finishes_data = [
        {
            "name": "Anodisé bronze",
            "description": "Finition anodisée couleur bronze",
            "price_coefficient": 1.25
        },
        {
            "name": "Anodisé naturel",
            "description": "Finition anodisée naturelle",
            "price_coefficient": 1.20
        },
        {
            "name": "Aluminium brut",
            "description": "Standard",
            "price_coefficient": 1.00
        },
        {
            "name": "Imitation bois chêne",
            "description": "Aspect bois chêne",
            "price_coefficient": 1.50
        },
        {
            "name": "Imitation bois noyer",
            "description": "Aspect bois noyer",
            "price_coefficient": 1.50
        },
        {
            "name": "RAL personnalisé",
            "description": "RAL XXXX",
            "price_coefficient": 1.40
        },
        {
            "name": "Thermolaqué blanc",
            "description": "RAL 9016",
            "price_coefficient": 1.30
        },
        {
            "name": "Thermolaqué gris anthracite",
            "description": "RAL 7016",
            "price_coefficient": 1.30
        },
        {
            "name": "Thermolaqué noir",
            "description": "RAL 9005",
            "price_coefficient": 1.30
        }
    ]
    
    for data in finishes_data:
        finish = Finish(company_id=company_id, **data)
        db.session.add(finish)
        print(f"  ✓ {data['name']}")
    
    print("\n🔩 Ajout des accessoires...")
    accessories_data = [
        {
            "name": "Charnière invisible (unité)",
            "unit_price": 18.00
        },
        {
            "name": "Charnière standard (unité)",
            "unit_price": 12.00
        },
        {
            "name": "Crémone renforcée",
            "unit_price": 55.00
        },
        {
            "name": "Crémone standard",
            "unit_price": 35.00
        },
        {
            "name": "Gond réglable (unité)",
            "unit_price": 15.00
        },
        {
            "name": "Joint d'étanchéité (mètre)",
            "unit_price": 8.00
        },
        {
            "name": "Poignée avec clé",
            "unit_price": 55.00
        },
        {
            "name": "Poignée design inox",
            "unit_price": 45.00
        },
        {
            "name": "Poignée standard aluminium",
            "unit_price": 28.00
        },
        {
            "name": "Rail de coulissement 2m",
            "unit_price": 65.00
        },
        {
            "name": "Rail de coulissement 3m",
            "unit_price": 90.00
        },
        {
            "name": "Serrure 3 points",
            "unit_price": 85.00
        },
        {
            "name": "Serrure 5 points",
            "unit_price": 125.00
        }
    ]
    
    for data in accessories_data:
        accessory = Accessory(
            company_id=company_id,
            name=data['name'],
            unit_price=data['unit_price'],
            incompatible_series=None
        )
        db.session.add(accessory)
        print(f"  ✓ {data['name']}")
    
    db.session.commit()
    
    print("\n" + "="*60)
    print("✅ ENTREPRISE DEMO CRÉÉE AVEC SUCCÈS!")
    print("="*60)
    print("\n📊 Résumé du catalogue:")
    print(f"  • Types de châssis: {len(chassis_types_data)}")
    print(f"  • Séries de profilés: {len(series_data)}")
    print(f"  • Types de vitrage: {len(glazing_data)}")
    print(f"  • Finitions: {len(finishes_data)}")
    print(f"  • Accessoires: {len(accessories_data)}")
    print("\n🔐 Connexion:")
    print("  • Nom d'utilisateur: demo")
    print("  • Mot de passe: demo123")
    print("  • Entreprise: Entreprise Demo")
    print("\n" + "="*60)
