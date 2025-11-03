# Boehringer Ingelheim Animal Health - Tableau Next & Agentforce Integration

This web application demonstrates the integration of Tableau Next dashboards with Salesforce Agentforce for Boehringer Ingelheim Animal Health's Sidekick Agents solution.

## Features

- **Tableau Next Dashboard Embedding**: Interactive analytics for territory management
- **Agentforce Integration**: AI-powered Sidekick Agent for sales rep productivity
- **Salesforce OAuth**: Secure authentication and authorization
- **Responsive Design**: Mobile-friendly interface for field representatives
- **Quick Actions**: Pre-configured prompts for common use cases

## Quick Start

### Prerequisites

1. Access to Heroku (login via Okta)
2. Heroku CLI installed
3. Salesforce Dreamforce org with proper setup
4. Tableau Next dashboard deployed with API name: `Sales_Cloud_Dashboard`

### Local Development

1. Clone this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   npm install
   ```

3. Copy environment variables:
   ```bash
   cp .env.example .env
   ```

4. Update `.env` with your Salesforce credentials

5. Run the application:
   ```bash
   python app.py
   ```

### Heroku Deployment

1. **Create Heroku App**:
   ```bash
   heroku login
   git init
   heroku apps:create your-app-name
   ```

2. **Set Environment Variables**:
   ```bash
   heroku config:set SALESFORCE_CLIENT_ID="your_client_id"
   heroku config:set SALESFORCE_CLIENT_SECRET="your_client_secret"
   heroku config:set HEROKU_APP_URL="https://your-app-name.herokuapp.com"
   ```

3. **Configure Buildpacks**:
   ```bash
   heroku buildpacks:set heroku/nodejs
   heroku buildpacks:add heroku/python
   ```

4. **Deploy**:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

## Salesforce Configuration Required

### 1. External Client App Setup
- **Name**: Boehringer Animal Health App
- **Distribution State**: Local
- **OAuth Scopes**: api, web, refresh_token, offline_access, lightning
- **Callback URL**: `https://your-app-name.herokuapp.com/callback`
- **Enable PKCE**: Yes

### 2. Agentforce Agent Configuration
- **Agent Type**: Agentforce Employee Agent
- **Description**: "Help people see and understand data with conversational analytics"
- **Topics**: Data Analysis topic
- **Target Entity**: Sales_Cloud_Dashboard

### 3. Session Settings
- **Trusted Domains**: Add your Heroku app URL for Lightning Out iframe

## Supported Use Cases

### Territory Planning & Analytics
- Weekly planning prioritization
- New clinic discovery (60-day lookback)
- Route optimization

### Loyalty Programs & Customer Management
- Vetsperity program enrollment tracking
- Tier progression analysis (within 5%)
- High-sales clinic program gaps

### Sales Performance & Competitive Intelligence
- Brand/SKU underperformance analysis
- Dispensing trend shifts
- Competitor comparison (Nexgard vs Simparica Trio)
- Top performer identification

### Operations & Training
- NBA performance tracking
- Training resource guidance

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│   Flask App      │◄──►│   Salesforce    │
│                 │    │   (Heroku)       │    │   (Tableau +    │
│ - Dashboard UI  │    │ - OAuth Handler  │    │    Agentforce)  │
│ - Chat Interface│    │ - API Proxy      │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## File Structure

```
web-app/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies
├── Procfile              # Heroku process configuration
├── runtime.txt           # Python version specification
├── .env.example          # Environment variables template
├── templates/
│   └── dashboard.html    # Main dashboard template
└── README.md            # This file
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SALESFORCE_CLIENT_ID` | OAuth Client ID from External Client App | Yes |
| `SALESFORCE_CLIENT_SECRET` | OAuth Client Secret | Yes |
| `HEROKU_APP_URL` | Full URL of your Heroku app | Yes |
| `SECRET_KEY` | Flask session secret key | Yes |
| `FLASK_ENV` | Environment (development/production) | No |

## Security Considerations

- All Salesforce communication uses OAuth 2.0 with PKCE
- Session data is encrypted using Flask's session management
- API calls are proxied through the Flask backend to avoid CORS issues
- No sensitive data is stored client-side

## Troubleshooting

### Common Issues

1. **"Authorization failed"**: Check OAuth configuration and callback URL
2. **"Not authenticated"**: Verify Salesforce credentials and session state
3. **Tableau dashboard not loading**: Confirm dashboard API name is `Sales_Cloud_Dashboard`
4. **Agentforce not responding**: Verify agent configuration and data analysis topic setup

### Debug Mode

Set `FLASK_ENV=development` for detailed error messages and auto-reload.

## Contact

- **Technical Contact**: Antoine Laviron
- **Project**: Sidekick Agents - Phase 1
- **Organization**: Boehringer Ingelheim Animal Health

## License

Internal use only - Boehringer Ingelheim proprietary.