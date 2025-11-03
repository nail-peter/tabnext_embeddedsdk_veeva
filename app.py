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
CORS(app)

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

    auth_url = f"{SALESFORCE_LOGIN_URL}/services/oauth2/authorize"
    params = {
        'response_type': 'code',
        'client_id': SALESFORCE_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'api web refresh_token offline_access lightning',
        'code_challenge': code_challenge,
        'code_challenge_method': 'S256'
    }

    auth_query = '&'.join([f"{k}={v}" for k, v in params.items()])
    return redirect(f"{auth_url}?{auth_query}")

@app.route('/callback')
def callback():
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

    # Exchange code for access token with PKCE
    token_url = f"{SALESFORCE_LOGIN_URL}/services/oauth2/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': SALESFORCE_CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'code': code,
        'code_verifier': code_verifier
    }

    response = requests.post(token_url, data=token_data)

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
        return f"Token exchange failed: {response.text}", 400

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

    # Use any existing dashboard ID from your org
    dashboard_id = os.environ.get('TABLEAU_DASHBOARD_ID', 'Performance_Overview_Full_Page')
    org_url = os.environ.get('SALESFORCE_ORG_URL', session.get('instance_url'))

    config = {
        'instanceUrl': session.get('instance_url'),
        'orgUrl': org_url,
        'dashboardId': dashboard_id,
        'accessToken': session.get('access_token'),
        'authCredential': session.get('access_token')
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)