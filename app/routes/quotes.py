from flask import Blueprint, request, jsonify
from app.models import Quote, ChassisType, ProfileSeries, GlazingType, Finish, Accessory, Config, Setting
from app.routes.auth import login_required
from app import db
from datetime import datetime
import json
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from flask import send_file

bp = Blueprint('quotes', __name__, url_prefix='/api/quotes')

@bp.route('/calculate', methods=['POST'])
@login_required
def calculate_price():
    data = request.json or {}
    
    # Validate and convert required fields
    try:
        width_mm = float(data.get('width', 0))
        height_mm = float(data.get('height', 0))
    except (ValueError, TypeError):
        return jsonify({'error': 'Width and height must be valid numbers'}), 400
    
    if width_mm <= 0 or height_mm <= 0:
        return jsonify({'error': 'Width and height must be greater than 0'}), 400
    
    chassis_type = data.get('chassisType')
    profile_series = data.get('profileSeries')
    glazing_type = data.get('glazingType')
    finish = data.get('finish')
    accessories = data.get('accessories', {})
    discount = data.get('discount', 0)
    
    if not chassis_type:
        return jsonify({'error': 'Chassis type is required'}), 400
    
    chassis_limits = ChassisType.query.filter_by(name=chassis_type).first()
    if not chassis_limits:
        return jsonify({'error': f'Invalid chassis type: {chassis_type}'}), 400
    
    if not (chassis_limits.min_width <= width_mm <= chassis_limits.max_width):
        return jsonify({'error': f'Width must be between {chassis_limits.min_width} and {chassis_limits.max_width} mm'}), 400
    if not (chassis_limits.min_height <= height_mm <= chassis_limits.max_height):
        return jsonify({'error': f'Height must be between {chassis_limits.min_height} and {chassis_limits.max_height} mm'}), 400
    
    surface_m2 = (width_mm * height_mm) / 1000000
    perimeter_m = 2 * (width_mm + height_mm) / 1000
    
    vat_config = Config.query.filter_by(key='vat_rate').first()
    loss_config = Config.query.filter_by(key='loss_coefficient').first()
    
    vat_rate = float(vat_config.value) / 100 if vat_config else 0.20
    loss_coef = float(loss_config.value) if loss_config else 1.1
    
    glazing_obj = GlazingType.query.filter_by(name=glazing_type).first()
    surface_price = glazing_obj.price_per_m2 if glazing_obj else 100.0
    
    profile_obj = ProfileSeries.query.filter_by(name=profile_series).first()
    linear_price = profile_obj.price_per_meter if profile_obj else 50.0
    
    finish_obj = Finish.query.filter_by(name=finish).first()
    finish_coef = finish_obj.price_coefficient if finish_obj else 1.0
    
    base_surface = surface_m2 * surface_price * loss_coef
    base_linear = perimeter_m * linear_price
    
    accessories_total = 0
    accessories_detail = []
    # accessories is now a dict: {accessoryName: quantity}
    for acc_name, quantity in accessories.items():
        acc_obj = Accessory.query.filter_by(name=acc_name).first()
        if acc_obj and quantity > 0:
            price = acc_obj.unit_price * quantity
            accessories_total += price
            accessories_detail.append({
                'name': acc_name,
                'quantity': quantity,
                'unit_price': round(acc_obj.unit_price, 2),
                'total_price': round(price, 2)
            })
    
    subtotal = (base_surface + base_linear + accessories_total) * finish_coef
    
    labor_config = Config.query.filter_by(key='labor_cost').first()
    labor_price = float(labor_config.value) if labor_config else 50.0
    
    total_before_discount = subtotal + labor_price
    discount_amount = total_before_discount * (discount / 100)
    total_ht = total_before_discount - discount_amount
    total_ttc = total_ht * (1 + vat_rate)
    
    breakdown = {
        'surface_m2': round(surface_m2, 3),
        'perimeter_m': round(perimeter_m, 2),
        'base_price': round(base_surface + base_linear, 2),
        'glazing_cost': round(base_surface, 2),
        'profile_cost': round(base_linear, 2),
        'accessories': accessories_detail,
        'accessories_cost': round(accessories_total, 2),
        'finish_coefficient': finish_coef,
        'finish_supplement': round((base_surface + base_linear) * (finish_coef - 1), 2),
        'subtotal': round(subtotal, 2),
        'labor': round(labor_price, 2),
        'total_before_discount': round(total_before_discount, 2),
        'discount_percent': discount,
        'discount_amount': round(discount_amount, 2),
        'total_ht': round(total_ht, 2),
        'vat_rate': round(vat_rate * 100, 2),
        'vat_amount': round(total_ttc - total_ht, 2),
        'total_price': round(total_ttc, 2)
    }
    
    return jsonify(breakdown)

@bp.route('', methods=['POST'])
@login_required
def create_quote():
    from flask import session
    data = request.json or {}
    breakdown = data.get('breakdown', {})
    
    company_id = session.get('company_id')
    
    today = datetime.now().strftime('%Y%m%d')
    quote_date = datetime.now().strftime('%Y-%m-%d')
    
    # Get the last quote number for today to avoid duplicates
    prefix = f"DEV-{today}-"
    if company_id:
        last_quote = Quote.query.filter(
            Quote.company_id == company_id,
            Quote.quote_number.like(f"{prefix}%")
        ).order_by(Quote.quote_number.desc()).first()
    else:
        last_quote = Quote.query.filter(
            Quote.company_id.is_(None),
            Quote.quote_number.like(f"{prefix}%")
        ).order_by(Quote.quote_number.desc()).first()
    
    if last_quote:
        # Extract the sequence number and increment
        last_number = int(last_quote.quote_number.split('-')[-1])
        quote_number = f"{prefix}{last_number + 1:04d}"
    else:
        # First quote of the day
        quote_number = f"{prefix}0001"
    
    # Store accessories as JSON with quantities
    accessories_data = data.get('accessories', {})
    
    # Create details with client info
    details = {
        **breakdown,
        'client_name': data.get('clientName', ''),
        'client_email': data.get('clientEmail', ''),
        'client_phone': data.get('clientPhone', ''),
        'client_notes': data.get('clientNotes', '')
    }
    
    quote = Quote(
        quote_number=quote_number,
        quote_date=quote_date,
        chassis_type=data.get('chassisType', ''),
        width=data.get('width', 0),
        height=data.get('height', 0),
        profile_series=data.get('profileSeries', ''),
        glazing_type=data.get('glazingType', ''),
        finish=data.get('finish', ''),
        accessories=json.dumps(accessories_data),
        discount_percent=data.get('discount', 0),
        price_ht=breakdown.get('total_ht', 0),
        price_ttc=breakdown.get('total_price', 0),
        details=json.dumps(details),
        company_id=company_id
    )
    
    db.session.add(quote)
    db.session.commit()
    
    return jsonify({'quote_number': quote_number, 'quote_id': quote.id})

@bp.route('/stats', methods=['GET'])
@login_required
def get_quotes_stats():
    from flask import session
    from datetime import timedelta
    company_id = session.get('company_id')
    role = session.get('role')
    
    if role == 'super_admin':
        query = Quote.query
    elif company_id:
        query = Quote.query.filter_by(company_id=company_id)
    else:
        query = Quote.query.filter_by(company_id=None)
    
    total = query.count()
    
    now = datetime.now()
    current_month = now.strftime('%Y-%m')
    this_month_quotes = query.filter(Quote.quote_date.like(f'{current_month}%')).all()
    this_month_count = len(this_month_quotes)
    this_month_amount = sum(q.price_ttc for q in this_month_quotes)
    
    week_start = (now - timedelta(days=now.weekday())).strftime('%Y-%m-%d')
    this_week_quotes = query.filter(Quote.quote_date >= week_start).all()
    this_week_count = len(this_week_quotes)
    this_week_amount = sum(q.price_ttc for q in this_week_quotes)
    
    if role == 'super_admin':
        total_amount = db.session.query(db.func.sum(Quote.price_ttc)).scalar() or 0
    else:
        total_amount = db.session.query(db.func.sum(Quote.price_ttc)).filter(
            Quote.company_id == company_id
        ).scalar() or 0
    
    total_items = 0
    top_client = None
    
    all_quotes = query.all()
    
    if all_quotes:
        client_count = {}
        
        for quote in all_quotes:
            try:
                details = json.loads(quote.details) if quote.details else {}
                items = details.get('items', [])
                total_items += len(items) if items else 1
                
                client_name = details.get('client_name', '')
                if client_name and client_name != '-':
                    client_count[client_name] = client_count.get(client_name, 0) + 1
            except:
                total_items += 1
        
        if client_count:
            top_client = max(client_count.items(), key=lambda x: x[1])[0]
    
    return jsonify({
        'total': total,
        'totalAmount': round(total_amount, 2),
        'thisMonth': this_month_count,
        'thisMonthAmount': round(this_month_amount, 2),
        'thisWeek': this_week_count,
        'thisWeekAmount': round(this_week_amount, 2),
        'totalItems': total_items,
        'topClient': top_client or '-'
    })

@bp.route('/recent', methods=['GET'])
@login_required
def get_recent_quotes():
    from flask import session
    limit = request.args.get('limit', 10, type=int)
    company_id = session.get('company_id')
    role = session.get('role')
    
    if role == 'super_admin':
        query = Quote.query
    elif company_id:
        query = Quote.query.filter_by(company_id=company_id)
    else:
        query = Quote.query.filter_by(company_id=None)
    
    quotes = query.order_by(Quote.created_at.desc()).limit(limit).all()
    
    result = []
    for quote in quotes:
        try:
            details = json.loads(quote.details) if quote.details else {}
            client_name = details.get('client_name', '-')
        except:
            client_name = '-'
        
        chassis_type_obj = ChassisType.query.filter_by(name=quote.chassis_type).first()
        chassis_type_name = chassis_type_obj.name if chassis_type_obj else quote.chassis_type
            
        result.append({
            'id': quote.id,
            'quote_number': quote.quote_number,
            'quote_date': quote.quote_date,
            'total_price': round(quote.price_ttc, 2),
            'chassis_type_name': chassis_type_name,
            'client_name': client_name,
            'created_at': quote.created_at.isoformat() if quote.created_at else None
        })
    
    return jsonify(result)

@bp.route('/<int:quote_id>', methods=['GET'])
@login_required
def get_quote(quote_id):
    from flask import session
    quote = Quote.query.get_or_404(quote_id)
    
    company_id = session.get('company_id')
    role = session.get('role')
    
    if role != 'super_admin' and quote.company_id != company_id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        details = json.loads(quote.details) if quote.details else {}
        accessories = json.loads(quote.accessories) if quote.accessories else {}
        
        return jsonify({
            'id': quote.id,
            'quote_number': quote.quote_number,
            'quote_date': quote.quote_date,
            'chassis_type': quote.chassis_type,
            'width': quote.width,
            'height': quote.height,
            'profile_series': quote.profile_series,
            'glazing_type': quote.glazing_type,
            'finish': quote.finish,
            'accessories': accessories,
            'discount_percent': quote.discount_percent,
            'price_ht': quote.price_ht,
            'price_ttc': quote.price_ttc,
            'details': details,
            'created_at': quote.created_at.isoformat() if quote.created_at else None
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:quote_id>', methods=['DELETE'])
@login_required
def delete_quote(quote_id):
    from flask import session
    quote = Quote.query.get_or_404(quote_id)
    
    company_id = session.get('company_id')
    role = session.get('role')
    
    if role != 'super_admin' and quote.company_id != company_id:
        return jsonify({'error': 'Access denied'}), 403
    
    try:
        db.session.delete(quote)
        db.session.commit()
        return jsonify({'message': 'Quote deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:quote_id>/pdf', methods=['GET'])
@login_required
def generate_pdf(quote_id):
    from flask import session
    quote = Quote.query.get_or_404(quote_id)
    
    company_id = session.get('company_id')
    role = session.get('role')
    
    if role != 'super_admin' and quote.company_id != company_id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get company info from settings
    company_settings = Setting.query.filter_by(section='company', company_id=quote.company_id).all()
    company_info = {s.key: s.value for s in company_settings}
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=15*mm, bottomMargin=20*mm)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Header with new layout
    breakdown = json.loads(quote.details)
    
    # Style for large quote number
    quote_number_style = ParagraphStyle(
        'QuoteNumber',
        parent=styles['Normal'],
        fontSize=22,
        textColor=colors.HexColor('#1a5490'),
        fontName='Helvetica-Bold',
        leading=26
    )
    
    # Company info (left side)
    company_name = company_info.get('company_name', 'MENUISERIE ALUMINIUM')
    company_address = company_info.get('company_address', '')
    company_phone = company_info.get('company_phone', '')
    company_email = company_info.get('company_email', '')
    
    company_text = f"<b>{company_name}</b><br/>"
    if company_address:
        company_text += f"{company_address}<br/>"
    if company_phone:
        company_text += f"Tél: {company_phone}<br/>"
    if company_email:
        company_text += f"Email: {company_email}"
    
    # Client info (right side)
    client_name = breakdown.get('client_name', '')
    client_email = breakdown.get('client_email', '')
    client_phone = breakdown.get('client_phone', '')
    
    client_text = "<b>CLIENT</b><br/>"
    if client_name:
        client_text += f"{client_name}<br/>"
    if client_phone:
        client_text += f"Tél: {client_phone}<br/>"
    if client_email:
        client_text += f"Email: {client_email}"
    
    # Date and validity (right side, bottom aligned)
    date_validity_style = ParagraphStyle(
        'DateValidity',
        parent=styles['Normal'],
        fontSize=9,
        alignment=TA_RIGHT
    )
    
    date_validity_text = f"<b>Date:</b> {quote.quote_date}<br/><b>Validité:</b> 30 jours"
    
    # Build header as 2-row, 2-column table
    # Row 1: Devis N° (left) | Date/Validité (right)
    # Row 2: Info Entreprise (left) | Info Client (right)
    
    header_data = [
        [
            Paragraph(f"Devis N°: {quote.quote_number}", quote_number_style),
            Paragraph(date_validity_text, date_validity_style)
        ],
        [
            Paragraph(company_text, styles['Normal']),
            Paragraph(client_text, styles['Normal'])
        ]
    ]
    
    header_table = Table(header_data, colWidths=[85*mm, 85*mm])
    header_table.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (0, -1), 0),
        ('RIGHTPADDING', (1, 0), (1, -1), 0),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTSIZE', (0, 1), (0, 1), 9),
        ('FONTSIZE', (1, 1), (1, 1), 9),
        ('TOPPADDING', (0, 1), (-1, 1), 8),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 10*mm))
    
    # Check if this is a multi-item quote
    items = breakdown.get('items', [])
    
    if items:
        # Multi-item quote
        elements.append(Paragraph('Articles du devis', styles['Heading2']))
        elements.append(Spacer(1, 5*mm))
        
        # Create summary table with all items
        summary_data = [['#', 'Type', 'Dimensions', 'Qté', 'Prix (MAD)']]
        
        for idx, item in enumerate(items, 1):
            item_type = item.get('chassisType', '')
            dimensions = f"{item.get('width', 0)} × {item.get('height', 0)} mm"
            item_breakdown = item.get('breakdown', {})
            quantity = item.get('quantity', 1)
            unit_price = item_breakdown.get('total_price', 0)
            total_price = unit_price * quantity
            price = f"{total_price:.2f}"
            summary_data.append([str(idx), item_type, dimensions, str(quantity), price])
        
        summary_table = Table(summary_data, colWidths=[12*mm, 55*mm, 45*mm, 15*mm, 35*mm])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 10*mm))
        
        # Detailed section for each item
        for idx, item in enumerate(items, 1):
            elements.append(Paragraph(f'Article {idx} - {item.get("chassisType", "")}', styles['Heading3']))
            elements.append(Spacer(1, 3*mm))
            
            accessories_dict = item.get('accessories', {})
            accessories_list = [f"{name} (Qté: {qty})" for name, qty in accessories_dict.items()]
            accessories_text = ', '.join(accessories_list) if accessories_list else 'Aucun'
            
            item_breakdown = item.get('breakdown', {})
            quantity = item.get('quantity', 1)
            details_data = [
                ['Type de châssis:', Paragraph(item.get('chassisType', ''), styles['Normal'])],
                ['Dimensions:', f"{item.get('width', 0)} mm × {item.get('height', 0)} mm"],
                ['Surface:', f"{item_breakdown.get('surface_m2', 0)} m²"],
                ['Périmètre:', f"{item_breakdown.get('perimeter_m', 0)} m"],
                ['Série de profilés:', Paragraph(item.get('profileSeries', ''), styles['Normal'])],
                ['Type de vitrage:', Paragraph(item.get('glazingType', ''), styles['Normal'])],
                ['Finition:', Paragraph(item.get('finish', ''), styles['Normal'])],
                ['Accessoires:', Paragraph(accessories_text, styles['Normal'])],
                ['Quantité:', str(quantity)]
            ]
            
            details_table = Table(details_data, colWidths=[50*mm, 120*mm])
            details_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
            ]))
            elements.append(details_table)
            elements.append(Spacer(1, 5*mm))
            
            # Price breakdown for this item
            item_breakdown = item.get('breakdown', {})
            unit_price = item_breakdown.get('total_price', 0)
            total_item_price = unit_price * quantity
            item_price_data = [
                ['Prix de base', f"{item_breakdown.get('base_price', 0):.2f} MAD"],
                ['Vitrage', f"{item_breakdown.get('glazing_cost', 0):.2f} MAD"],
                ['Accessoires', f"{item_breakdown.get('accessories_cost', 0):.2f} MAD"],
                ['Supplément finition', f"{item_breakdown.get('finish_supplement', 0):.2f} MAD"],
                ['Prix unitaire', f"{unit_price:.2f} MAD"],
                ['Quantité', f"× {quantity}"],
                ['Total article', f"{total_item_price:.2f} MAD"]
            ]
            
            item_price_table = Table(item_price_data, colWidths=[120*mm, 50*mm])
            item_price_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e0e0e0')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(item_price_table)
            elements.append(Spacer(1, 8*mm))
        
        # Global total
        elements.append(Paragraph('Total du devis', styles['Heading2']))
        elements.append(Spacer(1, 5*mm))
        
        total_price = sum(item.get('breakdown', {}).get('total_price', 0) * item.get('quantity', 1) for item in items)
        total_data = [
            ['TOTAL TTC', f"{total_price:.2f} MAD"]
        ]
        
        total_table = Table(total_data, colWidths=[120*mm, 50*mm])
        total_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#3B82F6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
        ]))
        elements.append(total_table)
        
    else:
        # Single-item quote (backwards compatibility)
        elements.append(Paragraph('Détails du châssis', styles['Heading2']))
        elements.append(Spacer(1, 5*mm))
        
        accessories_dict = json.loads(quote.accessories) if quote.accessories else {}
        accessories_list = [f"{name} (Qté: {qty})" for name, qty in accessories_dict.items()]
        accessories_text = ', '.join(accessories_list) if accessories_list else 'Aucun'
        
        details_data = [
            ['Type de châssis:', Paragraph(quote.chassis_type, styles['Normal'])],
            ['Dimensions:', f"{quote.width} mm × {quote.height} mm"],
            ['Surface:', f"{breakdown['surface_m2']} m²"],
            ['Périmètre:', f"{breakdown['perimeter_m']} m"],
            ['Série de profilés:', Paragraph(quote.profile_series, styles['Normal'])],
            ['Type de vitrage:', Paragraph(quote.glazing_type, styles['Normal'])],
            ['Finition:', Paragraph(quote.finish, styles['Normal'])],
            ['Accessoires:', Paragraph(accessories_text, styles['Normal'])]
        ]
        
        details_table = Table(details_data, colWidths=[50*mm, 120*mm])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f0f0f0')),
        ]))
        elements.append(details_table)
        elements.append(Spacer(1, 10*mm))
        
        elements.append(Paragraph('Détail du prix', styles['Heading2']))
        elements.append(Spacer(1, 5*mm))
        
        price_data = [
            ['Description', 'Montant (MAD)'],
            ['Prix de base', f"{breakdown.get('base_price', 0):.2f} MAD"],
            ['Vitrage', f"{breakdown.get('glazing_cost', 0):.2f} MAD"],
            ['Accessoires', f"{breakdown.get('accessories_cost', 0):.2f} MAD"],
            ['Supplément finition', f"{breakdown.get('finish_supplement', 0):.2f} MAD"],
            ['Total TTC', f"{breakdown.get('total_price', 0):.2f} MAD"]
        ]
        
        price_table = Table(price_data, colWidths=[120*mm, 50*mm])
        price_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e0e0e0')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(price_table)
    
    doc.build(elements)
    buffer.seek(0)
    
    pdf_size = len(buffer.getvalue())
    if pdf_size > 500000:
        return jsonify({'error': f'PDF too large ({pdf_size/1000:.1f}KB > 500KB limit)'}), 507
    
    return send_file(buffer, mimetype='application/pdf', as_attachment=True, download_name=f'devis_{quote.quote_number}.pdf')
