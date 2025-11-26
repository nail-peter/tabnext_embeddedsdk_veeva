# Salesforce Analytics Embedding Template

A minimal, plug-and-play template for embedding Salesforce Tableau Next Analytics and Agentforce into any web application, with optional Veeva CRM iframe integration.

## 🚀 Quick Start

1. **Clone this template**
2. **Configure your credentials** in `.env`
3. **Deploy to your hosting platform**
4. **Embed in Veeva CRM** (optional)

## 📋 Prerequisites

- Python 3.11+ (for Flask backend)
- Salesforce org with Analytics enabled
- Salesforce Connected App configured for OAuth

## 🏗️ Project Structure

```
salesforce-analytics-template/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment configuration
├── app.py                       # Flask application
├── templates/
│   ├── dashboard.html           # Main dashboard
│   └── components/
│       └── veeva-bridge.html    # Veeva CRM iframe component
├── static/js/                   # JavaScript files
├── scripts/setup.sh             # Setup script
└── docs/
    └── VEEVA-INTEGRATION.md     # Veeva CRM integration guide
```

## ⚙️ Configuration

Copy the environment template and configure your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Salesforce org details:

```env
# Required Salesforce Configuration
SALESFORCE_ORG_URL=https://your-org.my.salesforce.com
SALESFORCE_CLIENT_ID=your_connected_app_client_id
SALESFORCE_CLIENT_SECRET=your_connected_app_client_secret
TABLEAU_DASHBOARD_ID=your_dashboard_api_name
AGENTFORCE_AGENT_ID=Analytics_and_Visualization

# Application Configuration
APP_URL=http://localhost:5000
SECRET_KEY=your-secret-key

# Optional Veeva CRM Integration
VEEVA_INTEGRATION_ENABLED=false
```

## 🚀 Installation & Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run locally
python app.py
```

## 📊 What You Get

- **Tableau Next Dashboard**: Dynamic dashboard embedding with real-time data
- **Agentforce Analytics Agent**: AI-powered conversational analytics
- **Salesforce OAuth**: Secure authentication with PKCE
- **Responsive Design**: Works on desktop and mobile
- **Veeva CRM Ready**: Optional iframe integration

## 📱 Veeva CRM Integration

For pharmaceutical companies using Veeva CRM:

1. Set `VEEVA_INTEGRATION_ENABLED=true` in `.env`
2. Deploy your app to any hosting platform
3. Create a Visualforce page in Veeva CRM:

```html
<apex:page showHeader="false" standardStylesheets="false" sidebar="false">
    <div style="height: 100vh; width: 100%; margin: 0; padding: 0;">
        <iframe src="https://your-app.com/veeva/dashboard"
                width="100%" height="100%" frameborder="0">
        </iframe>
    </div>
</apex:page>
```

See `docs/VEEVA-INTEGRATION.md` for complete setup instructions.

## 🚀 Deployment

Deploy to any hosting platform that supports Python/Flask:
- AWS, Azure, Google Cloud
- On-premises servers
- PaaS platforms (Heroku, Railway, Render)

## 🔒 Security

- OAuth 2.0 with PKCE authentication
- Environment-based configuration
- CSP headers for iframe security

---

Built with ❤️ using Salesforce Analytics Embedding SDK v0.0.7-beta