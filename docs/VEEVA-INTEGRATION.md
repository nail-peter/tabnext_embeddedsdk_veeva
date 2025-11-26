# Veeva CRM Integration Guide

This guide shows how to embed your Salesforce Analytics dashboard directly into Veeva CRM pages using iframes.

## Overview

The template provides an iframe endpoint at `/veeva/dashboard` that can be embedded in Veeva CRM Visualforce pages. The dashboard will automatically show the appropriate data based on the user's Salesforce permissions and dashboard configuration.

## Setup

### 1. Enable Veeva Integration

In your `.env` file:

```bash
VEEVA_INTEGRATION_ENABLED=true
```

### 2. Create Visualforce Page in Veeva CRM

Create a new Visualforce page in Veeva CRM Setup:

**Setup → Visualforce Pages → New**

```html
<apex:page showHeader="false" standardStylesheets="false" sidebar="false">
    <div style="height: 100vh; width: 100%; margin: 0; padding: 0;">
        <iframe
            src="https://your-app.herokuapp.com/veeva/dashboard"
            width="100%"
            height="100%"
            frameborder="0"
            scrolling="no"
            allowtransparency="true">
        </iframe>
    </div>
</apex:page>
```

**Replace `https://your-app.herokuapp.com` with your actual deployment URL.**

### 3. Add to Veeva Page Layouts

Add the Visualforce page to your desired Veeva CRM page layouts:

1. Go to Setup → Page Layouts → Select your layout
2. Add Visualforce component
3. Select your analytics page

## How It Works

- User logs into Veeva CRM
- Clicks on page with embedded analytics
- Gets redirected to Salesforce OAuth if needed
- Dashboard loads with user's permissions and data access
- Salesforce handles all filtering and context automatically

## Testing

1. **Deploy your app** to an HTTPS URL
2. **Create the Visualforce page** with your app URL
3. **Add to a page layout** in Veeva CRM
4. **Test in Veeva CRM**

## Troubleshooting

**Iframe not loading:**
- Check HTTPS certificate is valid
- Verify URL is accessible from Veeva network

**Authentication issues:**
- Ensure Salesforce Connected App is configured
- Check OAuth callback URLs include your deployment domain
- Verify user has proper Salesforce permissions

### Testing Locally

For local development, use ngrok to create HTTPS tunnel:

```bash
# Start your local app
python app.py

# In another terminal, create HTTPS tunnel
ngrok http 5000

# Use the ngrok HTTPS URL in your Visualforce page
```

---

## Complete Example

```html
<apex:page showHeader="false" standardStylesheets="false" sidebar="false">
    <div style="height: 100vh; width: 100%; margin: 0; padding: 0;">
        <iframe
            src="https://mycompany-analytics.herokuapp.com/veeva/dashboard"
            width="100%"
            height="100%"
            frameborder="0"
            scrolling="no"
            allowtransparency="true">
        </iframe>
    </div>
</apex:page>
```

That's it! Your Salesforce Analytics will be embedded in Veeva CRM with automatic user context and permissions.