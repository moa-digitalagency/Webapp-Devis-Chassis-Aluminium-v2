#!/usr/bin/env python3
"""
Script to populate database with complete workflow data from screenshots
"""
import sys
sys.path.insert(0, '.')

from app import create_app, db
from app.models import ChassisType, ProfileSeries, GlazingType, Finish, Accessory

app = create_app()

with app.app_context():
    # Clear existing data
    print("Clearing existing catalog data...")
    Accessory.query.delete()
    Finish.query.delete()
    GlazingType.query.delete()
    ProfileSeries.query.delete()
    ChassisType.query.delete()
    
    # 1. Types de châssis (8 types from screenshot 1)
    print("Adding chassis types...")
    chassis_types = [
        ChassisType(name="Baie vitrée coulissante", description="Baie vitrée coulissante en aluminium", min_width=500, max_width=5000, min_height=500, max_height=3000),
        ChassisType(name="Châssis fixe", description="Châssis fixe / verrière", min_width=200, max_width=5000, min_height=200, max_height=3000),
        ChassisType(name="Fenêtre 1 vantail", description="Fenêtre aluminium avec un seul vantail ouvrant", min_width=300, max_width=1200, min_height=400, max_height=2000),
        ChassisType(name="Fenêtre 2 vantaux", description="Fenêtre aluminium avec deux vantaux ouvrants", min_width=600, max_width=2000, min_height=400, max_height=2000),
        ChassisType(name="Fenêtre oscillo-battant", description="Fenêtre aluminium avec système oscillo-battant", min_width=400, max_width=1500, min_height=500, max_height=2200),
        ChassisType(name="Porte avec imposte", description="Porte aluminium avec imposte vitrée", min_width=700, max_width=1200, min_height=2000, max_height=2800),
        ChassisType(name="Porte double", description="Porte aluminium à deux vantaux", min_width=1200, max_width=2000, min_height=2000, max_height=2600),
        ChassisType(name="Porte simple", description="Porte aluminium simple", min_width=700, max_width=1200, min_height=2000, max_height=2600),
    ]
    for ct in chassis_types:
        db.session.add(ct)
    
    # 2. Séries de profilés (3 series from screenshot 3)
    print("Adding profile series...")
    series = [
        ProfileSeries(name="Série Fine", description="Profilé élégant pour utilisation standard", price_per_meter=35.0),
        ProfileSeries(name="Série Renforcée", description="Profilé renforcé pour grandes dimensions", price_per_meter=45.0),
        ProfileSeries(name="Série Thermique", description="Profilé à rupture de pont thermique, isolation optimale", price_per_meter=55.0),
    ]
    for s in series:
        db.session.add(s)
    
    # 3. Types de vitrage (8 types from screenshot 4)
    print("Adding glazing types...")
    glazings = [
        GlazingType(name="10mm - Dépoli", description="Simple 10mm - Teinte Dépoli +25%", price_per_m2=102.0),
        GlazingType(name="10mm", description="Simple", price_per_m2=85.0),
        GlazingType(name="4/6/4", description="Double", price_per_m2=95.0),
        GlazingType(name="4mm", description="Simple", price_per_m2=45.0),
        GlazingType(name="6/8/6", description="Double", price_per_m2=115.0),
        GlazingType(name="6mm", description="Simple", price_per_m2=55.0),
        GlazingType(name="8mm", description="Simple", price_per_m2=70.0),
        GlazingType(name="Feuilleté 4mm", description="Feuilleté", price_per_m2=85.0),
        GlazingType(name="Sécurité 6mm", description="Sécurité", price_per_m2=120.0),
    ]
    for g in glazings:
        db.session.add(g)
    
    # 4. Accessoires (13 items from screenshot 5)
    print("Adding accessories...")
    accessories = [
        Accessory(name="Charnière invisible (unité)", unit_price=30.0, incompatible_series=""),
        Accessory(name="Charnière standard (unité)", unit_price=12.0, incompatible_series=""),
        Accessory(name="Crémone renforcée", unit_price=55.0, incompatible_series=""),
        Accessory(name="Crémone standard", unit_price=35.0, incompatible_series=""),
        Accessory(name="Gond réglable (unité)", unit_price=18.0, incompatible_series=""),
        Accessory(name="Joint d'étanchéité (mètre)", unit_price=8.0, incompatible_series=""),
        Accessory(name="Poignée avec clé", unit_price=55.0, incompatible_series=""),
        Accessory(name="Poignée design inox", unit_price=45.0, incompatible_series=""),
        Accessory(name="Poignée standard aluminium", unit_price=25.0, incompatible_series=""),
        Accessory(name="Rail de coulissement 2m", unit_price=65.0, incompatible_series=""),
        Accessory(name="Rail de coulissement 3m", unit_price=90.0, incompatible_series=""),
        Accessory(name="Serrure 3 points", unit_price=85.0, incompatible_series=""),
        Accessory(name="Serrure 5 points", unit_price=125.0, incompatible_series=""),
    ]
    for a in accessories:
        db.session.add(a)
    
    # 5. Finitions (10 options from screenshot 6)
    print("Adding finishes...")
    finishes = [
        Finish(name="Anodisé bronze", description="Anodisé", price_coefficient=1.25),
        Finish(name="Anodisé naturel", description="Anodisé", price_coefficient=1.20),
        Finish(name="Aluminium brut", description="Aluminium Brut - Standard", price_coefficient=1.0),
        Finish(name="Imitation bois chêne", description="Imitation Bois", price_coefficient=1.50),
        Finish(name="Imitation bois noyer", description="Imitation Bois", price_coefficient=1.50),
        Finish(name="RAL personnalisé", description="Thermolaqué - RAL XXXX", price_coefficient=1.40),
        Finish(name="Thermolaqué blanc", description="Thermolaqué - RAL 9016", price_coefficient=1.30),
        Finish(name="Thermolaqué gris anthracite", description="Thermolaqué - RAL 7016", price_coefficient=1.30),
        Finish(name="Thermolaqué noir", description="Thermolaqué - RAL 9005", price_coefficient=1.30),
    ]
    for f in finishes:
        db.session.add(f)
    
    db.session.commit()
    print("\n✅ Database populated successfully!")
    print(f"  - {len(chassis_types)} chassis types")
    print(f"  - {len(series)} profile series")
    print(f"  - {len(glazings)} glazing types")
    print(f"  - {len(accessories)} accessories")
    print(f"  - {len(finishes)} finishes")
