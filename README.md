# Salesforce Analytics Embedding SDK Template

A plug-and-play template for embedding Salesforce Tableau Next Analytics and Agentforce into any web application, with special integration patterns for Veeva CRM and pharmaceutical industry use cases.

## 🚀 Quick Start

1. **Clone this template**
2. **Configure your credentials** in `.env`
3. **Customize your industry data model**
4. **Deploy to your preferred platform**

## 📋 Prerequisites

- Node.js 18.x or higher
- Python 3.11.x (for Flask backend)
- Salesforce org with Analytics enabled
- Salesforce Connected App configured for OAuth

## 🏗️ Project Structure

```
salesforce-analytics-template/
├── README.md                          # This file
├── package.json                       # Node.js dependencies
├── requirements.txt                    # Python dependencies
├── .env.example                       # Environment configuration template
├── app.py                             # Flask backend server
├── config/
│   ├── industry-templates/            # Pre-built industry templates
│   │   ├── pharma.json                # Pharmaceutical template
│   │   ├── healthcare.json            # Healthcare template
│   │   └── generic.json               # Generic business template
│   └── veeva-integration.js           # Veeva CRM specific configurations
├── templates/
│   ├── dashboard.html                 # Main dashboard template
│   ├── components/
│   │   ├── analytics-dashboard.html   # Tableau Next component
│   │   ├── agentforce-chat.html      # Agentforce component
│   │   └── veeva-bridge.html         # Veeva CRM bridge component
│   └── layouts/
│       └── base.html                 # Base layout template
├── static/
│   ├── js/
│   │   ├── analytics-sdk.js          # Salesforce Analytics SDK
│   │   ├── template-core.js          # Template initialization logic
│   │   ├── veeva-integration.js      # Veeva CRM integration helpers
│   │   └── industry-adapters/
│   │       ├── pharma-adapter.js     # Pharmaceutical industry adapter
│   │       └── healthcare-adapter.js # Healthcare industry adapter
│   ├── css/
│   │   ├── template-styles.css       # Template styling
│   │   ├── industry-themes/
│   │   │   ├── pharma-theme.css      # Pharmaceutical styling
│   │   │   └── healthcare-theme.css  # Healthcare styling
│   │   └── veeva-optimized.css       # Veeva CRM optimized styles
│   └── assets/
├── scripts/
│   └── setup.sh                      # Quick setup script
└── docs/
    ├── CONFIGURATION.md              # Configuration guide
    ├── VEEVA-INTEGRATION.md          # Veeva CRM specific guide
    └── TROUBLESHOOTING.md            # Common issues and solutions
```

## ⚙️ Configuration

### 1. Environment Setup

Copy the environment template and configure your credentials:

```bash
cp .env.example .env
```

Edit `.env` with your Salesforce org details:

```env
# Salesforce Configuration
SALESFORCE_ORG_URL=https://your-org.my.salesforce.com
SALESFORCE_CLIENT_ID=your_connected_app_client_id
SALESFORCE_CLIENT_SECRET=your_connected_app_client_secret
TABLEAU_DASHBOARD_ID=your_dashboard_api_name
AGENTFORCE_AGENT_ID=your_agent_api_name

# Industry Template (pharma, healthcare, generic)
INDUSTRY_TEMPLATE=pharma

# Application Configuration
APP_URL=https://your-deployment-url.com
SECRET_KEY=your-secret-key

# Veeva CRM Integration (optional)
VEEVA_INTEGRATION_ENABLED=true
VEEVA_VAULT_URL=https://your-vault.veevavault.com
```

### 2. Industry Template Selection

Choose your industry template in `config/industry-templates/`:

- **pharma.json**: Pharmaceutical/Life Sciences
- **healthcare.json**: Healthcare/Medical Devices
- **generic.json**: General business use cases

### 3. Veeva CRM Integration

For Veeva CRM integration, additional configuration is available in `config/veeva-integration.js`.

## 🚀 Installation & Setup

### Quick Setup (Automated)

```bash
# Make setup script executable
chmod +x scripts/setup.sh

# Run setup script
./scripts/setup.sh
```

### Manual Setup

```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run locally
python app.py
```

## 🏥 Industry Templates

### Pharmaceutical Template
Pre-configured for pharmaceutical and life sciences companies:
- Sales performance dashboards
- Market share analytics
- Regulatory compliance tracking
- Clinical trial data visualization
- Territory management
- Competitive intelligence

### Healthcare Template
Optimized for healthcare and medical device companies:
- Patient outcome analytics
- Device performance monitoring
- Regulatory reporting
- Market access analytics
- Provider engagement tracking

### Generic Template
Flexible template for any industry:
- Sales and revenue analytics
- Performance dashboards
- Customer insights
- Operational metrics

## 📱 Veeva CRM Integration

This template includes special optimizations for Veeva CRM integration:

### Features
- **iframe-optimized layouts** for Veeva CRM embedding
- **Veeva Vault integration** for document management
- **Pharmaceutical data models** aligned with Veeva standards
- **Territory and account mapping** compatible with Veeva structures
- **Regulatory compliance** tracking and reporting

### Integration Options
1. **Embedded iFrame**: Embed analytics directly in Veeva CRM pages
2. **External Link**: Link from Veeva CRM to standalone analytics app
3. **API Integration**: Pull analytics data into Veeva CRM reports

See `docs/VEEVA-INTEGRATION.md` for detailed integration instructions.

## 📊 Analytics Components

### Tableau Next Dashboard
- Dynamic dashboard embedding
- Real-time data updates
- Interactive filters and controls
- Export capabilities
- Mobile responsive design

### Agentforce Analytics Agent
- Natural language query interface
- AI-powered insights
- Conversational analytics
- Pre-built industry prompts
- Custom agent configuration

## 🔧 Customization

### Adding Your Own Dashboards

1. Create your dashboard in Salesforce Analytics
2. Get the dashboard API name
3. Update `TABLEAU_DASHBOARD_ID` in `.env`
4. Optionally customize the layout in `templates/components/analytics-dashboard.html`

### Adding Custom Agentforce Agents

1. Configure your agent in Salesforce
2. Update `AGENTFORCE_AGENT_ID` in `.env`
3. Customize prompts in `static/js/industry-adapters/`

### Industry-Specific Customizations

1. Copy an existing template from `config/industry-templates/`
2. Modify the configuration for your specific use case
3. Update styling in `static/css/industry-themes/`
4. Add custom business logic in `static/js/industry-adapters/`

## 🚀 Deployment

Deploy this application to your preferred hosting platform:

- **Salesforce Experience Site**: Native Salesforce hosting
- **Veeva Cloud**: Pharmaceutical industry hosting
- **Enterprise Cloud**: AWS, Azure, Google Cloud
- **On-Premises**: Docker, Kubernetes, or traditional servers
- **PaaS Platforms**: Heroku, Railway, Render, etc.

The application is designed to work with any hosting platform that supports Python/Flask and Node.js.

## 📚 Documentation

- [Configuration Guide](docs/CONFIGURATION.md) - Detailed setup instructions
- [Veeva Integration](docs/VEEVA-INTEGRATION.md) - Veeva CRM integration details
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues and solutions

## 🔒 Security

- OAuth 2.0 with PKCE for secure authentication
- Environment-based secret management
- CSP headers for iframe security
- Veeva CRM security compliance
- GDPR/HIPAA considerations for healthcare data

## 🎯 Use Cases

### For Pharmaceutical Companies
- **Sales Rep Productivity**: Embedded analytics in Veeva CRM
- **Market Access**: Real-time market intelligence and competitive analysis
- **Clinical Operations**: Trial performance and regulatory compliance
- **Commercial Excellence**: Territory optimization and account prioritization

### For Healthcare Organizations
- **Provider Engagement**: Analytics embedded in provider portals
- **Patient Outcomes**: Real-time monitoring and reporting
- **Operational Efficiency**: Resource utilization and performance tracking
- **Regulatory Compliance**: Automated reporting and audit trails

### For Any Industry
- **Sales Performance**: Embedded analytics in CRM systems
- **Executive Dashboards**: Real-time business intelligence
- **Customer Analytics**: Behavior analysis and insights
- **Operational Metrics**: KPI monitoring and alerting

---

Built with ❤️ using Salesforce Analytics Embedding SDK v0.0.7-beta

## 📄 License

MIT License - see LICENSE file for details