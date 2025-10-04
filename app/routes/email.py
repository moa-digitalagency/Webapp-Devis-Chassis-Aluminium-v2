from flask import Blueprint, request, jsonify, session
from app.routes.auth import login_required
from app.models import Quote, User, AppSettings
from app import db
import os
import requests

bp = Blueprint('email', __name__)

def get_sendgrid_credentials():
    """Get SendGrid credentials from Replit connector"""
    hostname = os.getenv('REPLIT_CONNECTORS_HOSTNAME')
    x_replit_token = None
    
    if os.getenv('REPL_IDENTITY'):
        x_replit_token = 'repl ' + os.getenv('REPL_IDENTITY')
    elif os.getenv('WEB_REPL_RENEWAL'):
        x_replit_token = 'depl ' + os.getenv('WEB_REPL_RENEWAL')
    
    if not x_replit_token or not hostname:
        return None
    
    try:
        response = requests.get(
            f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=sendgrid',
            headers={
                'Accept': 'application/json',
                'X_REPLIT_TOKEN': x_replit_token
            }
        )
        
        if response.ok:
            data = response.json()
            items = data.get('items', [])
            if items and len(items) > 0:
                settings = items[0].get('settings', {})
                api_key = settings.get('api_key')
                from_email = settings.get('from_email')
                if api_key and from_email:
                    return {'api_key': api_key, 'from_email': from_email}
        return None
    except Exception as e:
        print(f"Error getting SendGrid credentials: {e}")
        return None

@bp.route('/send-quote', methods=['POST'])
@login_required
def send_quote_email():
    """Send quote via email using SendGrid"""
    try:
        data = request.get_json()
        quote_id = data.get('quote_id')
        recipient_email = data.get('recipient_email')
        recipient_name = data.get('recipient_name', '')
        message = data.get('message', '')
        
        if not quote_id or not recipient_email:
            return jsonify({'error': 'Quote ID and recipient email are required'}), 400
        
        # Get quote
        quote = Quote.query.get(quote_id)
        if not quote:
            return jsonify({'error': 'Quote not found'}), 404
        
        # Check access
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        if user.role != 'super_admin' and quote.company_id != user.company_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Get SendGrid credentials
        credentials = get_sendgrid_credentials()
        if not credentials:
            return jsonify({'error': 'SendGrid not configured'}), 500
        
        # Get app settings
        from_name_setting = AppSettings.query.filter_by(key='sendgrid_from_name').first()
        from_name = from_name_setting.value if from_name_setting else 'Devis Menuiserie'
        
        # Prepare email content
        subject = f'Devis #{quote.quote_number}'
        
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .quote-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background: #f5f5f5; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📄 Devis #{quote.quote_number}</h1>
                </div>
                <div class="content">
                    <p>Bonjour {recipient_name or 'cher client'},</p>
                    
                    {f'<p>{message}</p>' if message else ''}
                    
                    <p>Veuillez trouver ci-dessous le détail de votre devis :</p>
                    
                    <div class="quote-info">
                        <table>
                            <tr>
                                <th>Référence</th>
                                <td>{quote.quote_number}</td>
                            </tr>
                            <tr>
                                <th>Date</th>
                                <td>{quote.quote_date}</td>
                            </tr>
                            <tr>
                                <th>Type de châssis</th>
                                <td>{quote.chassis_type}</td>
                            </tr>
                            <tr>
                                <th>Dimensions</th>
                                <td>{quote.width} mm × {quote.height} mm</td>
                            </tr>
                            <tr>
                                <th>Série de profilés</th>
                                <td>{quote.profile_series}</td>
                            </tr>
                            <tr>
                                <th>Vitrage</th>
                                <td>{quote.glazing_type}</td>
                            </tr>
                            <tr>
                                <th>Finition</th>
                                <td>{quote.finish}</td>
                            </tr>
                            <tr>
                                <th style="font-size: 1.2em; color: #667eea;">Prix Total</th>
                                <td style="font-size: 1.2em; font-weight: bold; color: #667eea;">{quote.total_price:,.2f} MAD</td>
                            </tr>
                        </table>
                    </div>
                    
                    <p>Pour toute question ou modification, n'hésitez pas à nous contacter.</p>
                    
                    <p>Cordialement,<br><strong>{from_name}</strong></p>
                </div>
                <div class="footer">
                    <p>Ce devis est généré automatiquement par notre système de gestion.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email via SendGrid API
        sendgrid_url = 'https://api.sendgrid.com/v3/mail/send'
        headers = {
            'Authorization': f'Bearer {credentials["api_key"]}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'personalizations': [{
                'to': [{'email': recipient_email, 'name': recipient_name}],
                'subject': subject
            }],
            'from': {'email': credentials['from_email'], 'name': from_name},
            'content': [{'type': 'text/html', 'value': html_content}]
        }
        
        response = requests.post(sendgrid_url, headers=headers, json=payload)
        
        if response.status_code in [200, 202]:
            return jsonify({'success': True, 'message': 'Email sent successfully'})
        else:
            print(f"SendGrid error: {response.status_code} - {response.text}")
            return jsonify({'error': 'Failed to send email'}), 500
            
    except Exception as e:
        print(f"Error sending email: {e}")
        return jsonify({'error': str(e)}), 500

@bp.route('/test-connection', methods=['GET'])
@login_required
def test_sendgrid_connection():
    """Test SendGrid connection"""
    credentials = get_sendgrid_credentials()
    if credentials:
        return jsonify({
            'connected': True,
            'from_email': credentials['from_email']
        })
    else:
        return jsonify({'connected': False})
