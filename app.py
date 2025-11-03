import os
import json
import requests
import base64
import hashlib
import secrets
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

# Configure CORS for Salesforce embedding - more permissive for development
CORS(app,
     origins=['*'],  # Allow all origins for development
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization', 'X-Requested-With'],
     expose_headers=['Content-Range', 'X-Content-Range'])

# Add CSP headers for better embedding support
@app.after_request
def after_request(response):
    response.headers['Content-Security-Policy'] = (
        "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: blob: "
        "https://*.salesforce.com https://*.force.com https://*.lightning.force.com "
        "https://yg-agentforce-factory.lightning.force.com "
        "https://yg-agentforce-factory.my.salesforce.com; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' data: "
        "https://*.salesforce.com https://*.force.com https://*.lightning.force.com "
        "https://yg-agentforce-factory.lightning.force.com "
        "https://yg-agentforce-factory.my.salesforce.com; "
        "frame-src 'self' "
        "https://*.salesforce.com https://*.force.com https://*.lightning.force.com "
        "https://yg-agentforce-factory.lightning.force.com "
        "https://yg-agentforce-factory.my.salesforce.com; "
        "style-src 'self' 'unsafe-inline' "
        "https://*.salesforce.com https://*.force.com https://*.lightning.force.com; "
        "img-src 'self' data: https://*.salesforce.com https://*.force.com; "
        "connect-src 'self' https://*.salesforce.com https://*.force.com"
    )
    # Add headers to allow iframe embedding
    # Remove X-Frame-Options to allow iframe embedding
    if 'X-Frame-Options' in response.headers:
        del response.headers['X-Frame-Options']
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

# Salesforce OAuth Configuration
SALESFORCE_CLIENT_ID = os.environ.get('SALESFORCE_CLIENT_ID')
SALESFORCE_CLIENT_SECRET = os.environ.get('SALESFORCE_CLIENT_SECRET')
SALESFORCE_LOGIN_URL = os.environ.get('SALESFORCE_LOGIN_URL', 'https://login.salesforce.com')
REDIRECT_URI = os.environ.get('APP_URL', 'http://localhost:5000') + '/callback'

@app.route('/')
def index():
    """Main landing page with login option"""
    if 'access_token' in session:
        return redirect(url_for('dashboard'))

    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Main dashboard page with Tableau Next and Agentforce integration"""
    if 'access_token' not in session:
        return redirect(url_for('index'))

    return render_template('dashboard.html',
                         user_info=session.get('user_info'),
                         instance_url=session.get('instance_url'))

@app.route('/login')
def login():
    """Initiate Salesforce OAuth flow with PKCE"""
    # Generate PKCE code verifier and challenge
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')

    # Store code verifier in session for callback
    session['code_verifier'] = code_verifier
    print(SALESFORCE_LOGIN_URL)
    # Use org-specific login URL for external client apps
    auth_url = f"https://yg-agentforce-factory.my.salesforce.com/services/oauth2/authorize"
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
    print("Manuel")
    """Handle Salesforce OAuth callback with PKCE"""
    code = request.args.get('code')
    error = request.args.get('error')

    if error:
        error_description = request.args.get('error_description', '')
        return f"Authorization failed: {error} - {error_description}", 400

    if not code:
        return "Authorization failed: No authorization code received", 400

    # Get code verifier from session
    code_verifier = session.get('code_verifier')
    if not code_verifier:
        return "Authorization failed: Missing PKCE code verifier", 400

    # Exchange code for access token with PKCE - use org-specific URL
    token_url = f"https://yg-agentforce-factory.my.salesforce.com/services/oauth2/token"

    # Try PKCE-only flow first (recommended for your setup)
    token_data_pkce = {
        'grant_type': 'authorization_code',
        'client_id': SALESFORCE_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'code': code,
        'code_verifier': code_verifier
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }

    print(f"Token URL: {token_url}")
    print(f"PKCE Token data: {token_data_pkce}")

    response = requests.post(token_url, data=token_data_pkce, headers=headers)

    # If PKCE-only fails, try with client_secret as fallback
    if response.status_code != 200 and SALESFORCE_CLIENT_SECRET:
        print("PKCE-only failed, trying with client_secret...")

        token_data_secret = {
            'grant_type': 'authorization_code',
            'client_id': SALESFORCE_CLIENT_ID,
            'client_secret': SALESFORCE_CLIENT_SECRET,
            'redirect_uri': REDIRECT_URI,
            'code': code,
            'code_verifier': code_verifier
        }

        print(f"Secret Token data: {token_data_secret}")
        response = requests.post(token_url, data=token_data_secret, headers=headers)

    if response.status_code == 200:
        token_info = response.json()
        session['access_token'] = token_info['access_token']
        session['instance_url'] = token_info['instance_url']
        session['refresh_token'] = token_info.get('refresh_token')

        # Get user info
        user_info_response = requests.get(
            token_info['id'],
            headers={'Authorization': f"Bearer {token_info['access_token']}"}
        )

        if user_info_response.status_code == 200:
            session['user_info'] = user_info_response.json()

        return redirect(url_for('dashboard'))
    else:
        # Enhanced error debugging
        print(f"Token exchange failed. Status: {response.status_code}")
        print(f"Response: {response.text}")
        print(f"Response headers: {response.headers}")
        return f"Token exchange failed (Status {response.status_code}): {response.text}", 400

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

    # Use the correct dashboard ID and org URL for yg-agentforce-factory
    dashboard_id = os.environ.get('TABLEAU_DASHBOARD_ID', 'Performance_Overview_Full_Page')
    org_url = os.environ.get('SALESFORCE_ORG_URL', 'https://yg-agentforce-factory.lightning.force.com')

    config = {
        'instanceUrl': session.get('instance_url'),
        'orgUrl': org_url,
        'dashboardId': dashboard_id,
        'accessToken': session.get('access_token'),
        'authCredential': session.get('access_token'),
        'sessionId': session.get('access_token'),
        'apiVersion': '58.0'
    }

    return jsonify(config)

@app.route('/api/agentforce-proxy', methods=['POST'])
def agentforce_proxy():
    """Proxy requests to Salesforce Agentforce API"""
    if 'access_token' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    # Forward request to Salesforce Agentforce
    headers = {
        'Authorization': f"Bearer {session['access_token']}",
        'Content-Type': 'application/json'
    }

    # Configurable Agentforce endpoint
    agentforce_endpoint = os.environ.get('AGENTFORCE_ENDPOINT', '/services/data/v58.0/analytics/agent')
    agentforce_url = f"{session['instance_url']}{agentforce_endpoint}"

    response = requests.post(
        agentforce_url,
        headers=headers,
        json=request.get_json()
    )

    return jsonify(response.json()), response.status_code

@app.route('/api/dashboard-proxy')
def dashboard_proxy():
    """Proxy endpoint for dashboard embedding (experimental)"""
    if 'access_token' not in session:
        return "Authentication required", 401

    dashboard_id = request.args.get('dashboardId')
    token = request.args.get('token', session.get('access_token'))

    if not dashboard_id:
        return "Dashboard ID required", 400

    # Create a simple HTML page that attempts to load the dashboard
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Tableau Dashboard Proxy</title>
        <style>
            body {{ margin: 0; padding: 20px; font-family: Arial, sans-serif; }}
            .message {{ text-align: center; padding: 40px; color: #666; }}
            .redirect-link {{
                display: inline-block;
                background: #1B96FF;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                border-radius: 6px;
                margin-top: 20px;
            }}
            .redirect-link:hover {{ background: #0678d4; }}
        </style>
    </head>
    <body>
        <div class="message">
            <h2>Dashboard Access</h2>
            <p>Due to Salesforce security policies, the dashboard cannot be embedded directly.</p>
            <p>Click the link below to open the dashboard in Salesforce:</p>
            <a href="{session.get('instance_url')}/secur/frontdoor.jsp?sid={token}&retURL={'/analytics/wave/dashboard/' + dashboard_id}"
               target="_blank"
               class="redirect-link">
                Open Dashboard in Salesforce
            </a>
            <p style="margin-top: 30px; font-size: 14px; color: #888;">
                Dashboard ID: {dashboard_id}
            </p>
        </div>
    </body>
    </html>
    """

    response = app.response_class(
        response=html_content,
        status=200,
        mimetype='text/html'
    )

    # Add headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)