# NEPS Mock REDCap API

Standalone mock REDCap API service for NEPS Digital development.

## Deploy to Render

1. Push this repo to GitHub
2. Connect repo to Render (New Web Service → Build and deploy from Git repository)
3. Render reads `render.yaml` and deploys automatically

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| `/api/participants` | GET | List participants |
| `/api/participants/{id}` | GET | Get participant |
| `/api/monthly-reports` | GET | List monthly reports |
| `/api/comprehensive-waves` | GET | List comprehensive waves |
| `/api/distress-screenings` | GET | Get safeguarding alerts |
| `/api/wp6-sessions/{id}` | GET | Get WP6 sessions |
| `/api/consent/{id}` | GET | Get consent record |
| `/api/referrals` | POST | Create referral |
| `/api/stats` | GET | Project statistics |
| `/api/export/records` | GET | Export all records |
| `/api/field-mapping` | GET | Current field mapping |

## Team Configuration

Set this in your `.env`:

```bash
REDCAP_API_URL=https://your-render-url.onrender.com/api
REDCAP_API_TOKEN=mock_token_neps_2025
```

When real REDCap is ready, change only the URL and token.
