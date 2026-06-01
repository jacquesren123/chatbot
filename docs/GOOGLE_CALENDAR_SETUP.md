# Google Calendar OAuth Integration Guide

## Overview

This guide explains how to implement Google Calendar OAuth 2.0 for the scheduling service, allowing businesses to connect their Google Calendar for appointment booking.

## Architecture

### Multi-Tenant OAuth Flow
Each tenant (business) needs their own Google Calendar connection:
1. Business admin initiates OAuth flow from dashboard
2. Google redirects to consent screen
3. User grants calendar access
4. Store refresh token per tenant in database
5. Use refresh token to access calendar API

## Setup Steps

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "Chatbot Platform Calendar"
3. Enable Google Calendar API:
   - APIs & Services → Library
   - Search "Google Calendar API"
   - Click Enable

### 2. Configure OAuth Consent Screen

1. APIs & Services → OAuth consent screen
2. Choose "External" (for multi-tenant SaaS)
3. Fill in:
   - App name: "Your Chatbot Platform"
   - User support email: your email
   - Developer contact: your email
4. Add scopes:
   - `https://www.googleapis.com/auth/calendar.readonly` (view calendar)
   - `https://www.googleapis.com/auth/calendar.events` (create events)
5. Add test users (during development)
6. Save and continue

### 3. Create OAuth Credentials

1. APIs & Services → Credentials
2. Create Credentials → OAuth 2.0 Client ID
3. Application type: Web application
4. Name: "Chatbot Platform Web"
5. Authorized redirect URIs:
   - `http://localhost:8000/api/v1/auth/google/callback` (dev)
   - `https://yourdomain.com/api/v1/auth/google/callback` (prod)
6. Save and download JSON credentials

### 4. Update Environment Variables

Add to `.env`:
```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/v1/auth/google/callback
```

## Database Schema Changes

Add table to store OAuth tokens per tenant:

```sql
CREATE TABLE tenant_integrations (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
    integration_type VARCHAR(50) NOT NULL, -- 'google_calendar'
    access_token TEXT,
    refresh_token TEXT NOT NULL,
    token_expiry TIMESTAMP,
    calendar_id VARCHAR(255) DEFAULT 'primary',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(tenant_id, integration_type)
);
```

## Implementation

### 1. OAuth Endpoints (API Gateway)

```python
# services/api-gateway/main.py

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials

SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events'
]

@app.get("/api/v1/auth/google/connect")
async def google_connect(tenant_id: str):
    """Initiate OAuth flow for tenant"""
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=SCOPES,
        redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
    )
    
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
        state=tenant_id  # Pass tenant_id in state
    )
    
    return {"authorization_url": authorization_url}

@app.get("/api/v1/auth/google/callback")
async def google_callback(code: str, state: str):
    """Handle OAuth callback and store tokens"""
    tenant_id = state
    
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI")],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=SCOPES,
        redirect_uri=os.getenv("GOOGLE_REDIRECT_URI")
    )
    
    flow.fetch_token(code=code)
    credentials = flow.credentials
    
    # Store in database
    async with get_db() as db:
        integration = db.query(TenantIntegration).filter_by(
            tenant_id=tenant_id,
            integration_type='google_calendar'
        ).first()
        
        if integration:
            integration.access_token = credentials.token
            integration.refresh_token = credentials.refresh_token
            integration.token_expiry = credentials.expiry
        else:
            integration = TenantIntegration(
                tenant_id=tenant_id,
                integration_type='google_calendar',
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_expiry=credentials.expiry
            )
            db.add(integration)
        
        db.commit()
    
    return {"status": "connected", "message": "Google Calendar connected successfully"}
```

### 2. Update Scheduling Service

```python
# services/scheduling-service/main.py

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

class SchedulingService:
    async def _get_credentials(self, tenant_id: str):
        """Get valid credentials for tenant"""
        async with get_db() as db:
            integration = db.query(TenantIntegration).filter_by(
                tenant_id=tenant_id,
                integration_type='google_calendar',
                is_active=True
            ).first()
            
            if not integration:
                return None
            
            credentials = Credentials(
                token=integration.access_token,
                refresh_token=integration.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=os.getenv("GOOGLE_CLIENT_ID"),
                client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
                scopes=SCOPES
            )
            
            # Refresh if expired
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
                
                # Update database
                integration.access_token = credentials.token
                integration.token_expiry = credentials.expiry
                db.commit()
            
            return credentials
    
    async def get_availability(self, tenant_id: str, start_date: datetime, end_date: datetime):
        """Get availability from Google Calendar"""
        credentials = await self._get_credentials(tenant_id)
        
        if not credentials:
            return self._generate_mock_availability(start_date, end_date, 30)
        
        service = build('calendar', 'v3', credentials=credentials)
        
        # Rest of implementation...
```

### 3. Add Database Model

```python
# shared/models/integration.py

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from shared.database import Base

class TenantIntegration(Base):
    __tablename__ = "tenant_integrations"
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    integration_type = Column(String(50), nullable=False)
    access_token = Column(Text)
    refresh_token = Column(Text, nullable=False)
    token_expiry = Column(DateTime)
    calendar_id = Column(String(255), default="primary")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

## Frontend Integration (Dashboard)

```javascript
// In business dashboard
async function connectGoogleCalendar() {
    const tenantId = getCurrentTenantId();
    
    const response = await fetch(`/api/v1/auth/google/connect?tenant_id=${tenantId}`);
    const data = await response.json();
    
    // Open OAuth popup
    window.location.href = data.authorization_url;
}

// Show connection status
async function checkCalendarConnection() {
    const response = await fetch('/api/v1/integrations/google-calendar/status');
    const data = await response.json();
    
    if (data.connected) {
        document.getElementById('calendar-status').textContent = '✅ Connected';
    } else {
        document.getElementById('calendar-status').textContent = '❌ Not Connected';
    }
}
```

## Testing

### 1. Test OAuth Flow
```bash
# Start services
./start-all.sh

# Open browser
http://localhost:8000/api/v1/auth/google/connect?tenant_id=tenant1

# Complete OAuth flow
# Check database for stored tokens
```

### 2. Test Calendar API
```bash
curl -X POST http://localhost:8004/availability \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant1",
    "start_date": "2024-01-20T00:00:00Z",
    "end_date": "2024-01-21T00:00:00Z",
    "duration_minutes": 30
  }'
```

## Security Best Practices

1. **Store tokens encrypted** - Use database encryption for refresh tokens
2. **Validate state parameter** - Prevent CSRF attacks
3. **Use HTTPS in production** - Required for OAuth
4. **Implement token rotation** - Refresh tokens regularly
5. **Scope minimization** - Only request needed permissions
6. **Revocation endpoint** - Allow users to disconnect
7. **Audit logging** - Log all calendar access

## Production Checklist

- [ ] Move to verified OAuth app (remove test mode)
- [ ] Add privacy policy URL
- [ ] Add terms of service URL
- [ ] Implement token encryption
- [ ] Add HTTPS redirect URIs
- [ ] Set up monitoring for token expiry
- [ ] Implement graceful degradation (fallback to mock)
- [ ] Add user-facing disconnect button
- [ ] Test token refresh flow
- [ ] Add rate limiting for OAuth endpoints

## Troubleshooting

### "redirect_uri_mismatch" error
- Ensure redirect URI in code matches Google Console exactly
- Include http:// or https://
- No trailing slashes

### "invalid_grant" error
- Refresh token expired or revoked
- User needs to reconnect
- Show reconnect prompt in dashboard

### Token refresh fails
- Check client_id and client_secret
- Ensure refresh_token is stored
- Verify token_uri is correct

## Alternative: Service Account (Not Recommended for SaaS)

Service accounts work for single-tenant but not multi-tenant SaaS:
- Each business would need to share their calendar with service account
- Less secure and user-friendly
- Use OAuth 2.0 instead

## Resources

- [Google Calendar API Docs](https://developers.google.com/calendar/api/guides/overview)
- [OAuth 2.0 for Web Apps](https://developers.google.com/identity/protocols/oauth2/web-server)
- [Python Quickstart](https://developers.google.com/calendar/api/quickstart/python)
