"""
Salesforce Analytics Embedding Template
Simple Flask application for embedding Tableau Next dashboards and Agentforce agents

Features:
- Salesforce OAuth 2.0 with PKCE authentication
- Tableau Next dashboard embedding
- Agentforce analytics agent integration
- Optional Veeva CRM integration support
"""

import os
import logging
import requests
import base64
import hashlib
import secrets
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Configure CORS for Salesforce embedding
CORS(app, supports_credentials=True)

# Configuration
SALESFORCE_CLIENT_ID = os.environ.get('SALESFORCE_CLIENT_ID')
SALESFORCE_CLIENT_SECRET = os.environ.get('SALESFORCE_CLIENT_SECRET')
SALESFORCE_ORG_URL = os.environ.get('SALESFORCE_ORG_URL')
TABLEAU_DASHBOARD_ID = os.environ.get('TABLEAU_DASHBOARD_ID')
AGENTFORCE_AGENT_ID = os.environ.get('AGENTFORCE_AGENT_ID', 'Analytics_and_Visualization')
COMPANY_NAME = os.environ.get('COMPANY_NAME', 'Your Organization')
VEEVA_INTEGRATION = os.environ.get('VEEVA_INTEGRATION_ENABLED', 'false').lower() == 'true'
REDIRECT_URI = os.environ.get('APP_URL', 'http://localhost:5000') + '/callback'

# Security headers
@app.after_request
def after_request(response):
    # CSP for analytics embedding
    csp_policy = (
        "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob: "
        "https://*.salesforce.com https://*.force.com https://*.lightning.force.com; "
        "frame-src 'self' https://*.salesforce.com https://*.force.com; "
    )

    if SALESFORCE_ORG_URL:
        csp_policy += f" {SALESFORCE_ORG_URL};"

    response.headers['Content-Security-Policy'] = csp_policy
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # Allow iframe embedding
    if 'X-Frame-Options' in response.headers:
        del response.headers['X-Frame-Options']

    return response

@app.route('/')
def index():
    """Main landing page"""
    if 'access_token' in session:
        return redirect(url_for('dashboard'))

    return render_template('index.html', company_name=COMPANY_NAME)

@app.route('/dashboard')
def dashboard():
    """Main dashboard with analytics"""
    if 'access_token' not in session:
        return redirect(url_for('login'))

    return render_template('dashboard.html',
                         user_info=session.get('user_info'),
                         company_name=COMPANY_NAME,
                         veeva_integration=VEEVA_INTEGRATION)

@app.route('/veeva/dashboard')
def veeva_dashboard():
    """Veeva CRM optimized dashboard (iframe-friendly)"""
    if not VEEVA_INTEGRATION:
        return "Veeva integration not enabled", 404

    # Check authentication
    if 'access_token' not in session:
        return redirect(url_for('login'))

    return render_template('veeva-bridge.html')

@app.route('/login')
def login():
    """Initiate Salesforce OAuth flow with PKCE"""
    # Generate PKCE code verifier and challenge
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')

    session['code_verifier'] = code_verifier

    # OAuth URL
    auth_url = f"{SALESFORCE_ORG_URL}/services/oauth2/authorize"
    params = {
        'response_type': 'code',
        'client_id': SALESFORCE_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'api web refresh_token offline_access lightning wave_api',
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }

    auth_query = '&'.join([f"{k}={v}" for k, v in params.items()])
    return redirect(f"{auth_url}?{auth_query}")

@app.route('/callback')
def callback():
    """Handle Salesforce OAuth callback"""
    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        logger.error(f"OAuth error: {error}")
        return f"Authorization failed: {error}", 400

    if not code:
        return "Authorization failed: No code received", 400

    code_verifier = session.get('code_verifier')
    if not code_verifier:
        return "Authorization failed: Missing code verifier", 400

    # Exchange code for token
    token_url = f"{SALESFORCE_ORG_URL}/services/oauth2/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': SALESFORCE_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'code': code,
        'code_verifier': code_verifier
    }

    if SALESFORCE_CLIENT_SECRET:
        token_data['client_secret'] = SALESFORCE_CLIENT_SECRET

    try:
        response = requests.post(token_url, data=token_data, timeout=30)
        response.raise_for_status()

        token_info = response.json()
        session['access_token'] = token_info['access_token']
        session['instance_url'] = token_info['instance_url']
        session['refresh_token'] = token_info.get('refresh_token')

        # Get user info
        user_response = requests.get(
            token_info['id'],
            headers={'Authorization': f"Bearer {token_info['access_token']}"},
            timeout=30
        )

        if user_response.status_code == 200:
            session['user_info'] = user_response.json()

        return redirect(url_for('dashboard'))

    except Exception as e:
        logger.error(f"Token exchange failed: {e}")
        return f"Authentication failed: {e}", 500

@app.route('/logout')
def logout():
    """Clear session and redirect to home"""
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/tableau-config')
def tableau_config():
    """Provide Tableau embedding configuration"""
    if 'access_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        access_token = session.get('access_token')
        instance_url = session.get('instance_url')

        # Generate frontdoor URL
        frontdoor_url = f"{instance_url}/services/oauth2/singleaccess"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        try:
            response = requests.post(frontdoor_url, headers=headers, timeout=10)
            if response.status_code == 200:
                frontdoor_data = response.json()
                frontdoor_uri = frontdoor_data.get('frontdoor_uri')
            else:
                frontdoor_uri = f"{instance_url}/secur/frontdoor.jsp?sid={access_token}"
        except:
            frontdoor_uri = f"{instance_url}/secur/frontdoor.jsp?sid={access_token}"

        config = {
            'authCredential': frontdoor_uri,
            'orgUrl': instance_url,
            'dashboardId': TABLEAU_DASHBOARD_ID,
            'agentId': AGENTFORCE_AGENT_ID,
            'veevaIntegration': VEEVA_INTEGRATION
        }

        return jsonify(config)

    except Exception as e:
        logger.error(f"Config error: {e}")
        return jsonify({'error': 'Configuration error'}), 500

@app.route('/api/agentforce-proxy', methods=['POST'])
def agentforce_proxy():
    """Proxy requests to Salesforce Agentforce API"""
    if 'access_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    headers = {
        'Authorization': f"Bearer {session['access_token']}",
        'Content-Type': 'application/json'
    }

    agentforce_url = f"{session['instance_url']}/services/data/v58.0/analytics/agent"

    try:
        response = requests.post(
            agentforce_url,
            headers=headers,
            json=request.get_json(),
            timeout=30
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        logger.error(f"Agentforce proxy error: {e}")
        return jsonify({'error': 'Service unavailable'}), 503

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Validate required config
    required_vars = ['SALESFORCE_CLIENT_ID', 'SALESFORCE_ORG_URL', 'TABLEAU_DASHBOARD_ID']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]

    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        logger.error("Check your .env file configuration")
        exit(1)

    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'

    logger.info(f"Starting Salesforce Analytics Template on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)