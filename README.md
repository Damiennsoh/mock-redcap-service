# NEPS Mock REDCap API

Standalone mock REDCap API service for NEPS Digital development. It provides realistic longitudinal youth mental health data for Ghana, Sierra Leone, and Tanzania.

## Deployed Service

The mock API is currently deployed on Render!
- **URL**: https://mock-redcap-service.onrender.com
- **API Base Path**: https://mock-redcap-service.onrender.com/api
- **Docs**: https://mock-redcap-service.onrender.com/docs
- **Health Check**: https://mock-redcap-service.onrender.com/health

## 🧠 Semantically Correlated NLP Dataset (v0.2.0)

To resolve issues with random label noise in ML training, a **2000-row semantically correlated NLP dataset** has been integrated directly into the service. 

Instead of random label assignment:
- **Sentiment scores** (`sentiment_score` & `sentiment_manual`) are computed from positive/negative word counts in the actual narrative.
- **Severity levels** (`severity_level`) are determined by crisis word presence and sentiment thresholds.
- **Clinical statuses** (`clinical_status`) are mapped from specific anxiety, depression, and stress word patterns.
- **Thematic codes** (`thematic_codes`) are extracted directly from context keywords.

### Seed Dataset Files (Root Directory)
The repository contains the following pre-generated files for the ML/AI and Data Platform teams:
1. **[NEPS_NLP_Mock_Dataset_2000.json](file:///d:/COMPUTER_SCIENCE/NEPS-PORTAL/mock-redcap-service/NEPS_NLP_Mock_Dataset_2000.json)**: The full 2000-record dataset in JSON format. Loaded directly at startup.
2. **[NEPS_NLP_Mock_Dataset_2000.csv](file:///d:/COMPUTER_SCIENCE/NEPS-PORTAL/mock-redcap-service/NEPS_NLP_Mock_Dataset_2000.csv)**: Spreadsheet-friendly version of the dataset.
3. **[NEPS_NLP_Dataset_Summary.json](file:///d:/COMPUTER_SCIENCE/NEPS-PORTAL/mock-redcap-service/NEPS_NLP_Dataset_Summary.json)**: Summary report outlining label and theme distributions (15+ emotions, 15+ themes).

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| `/api/participants` | GET | List participants |
| `/api/participants/{id}` | GET | Get participant |
| `/api/participants/{id}/monthly-reports` | GET | Get participant's monthly reports |
| `/api/participants/{id}/comprehensive-waves` | GET | Get participant's comprehensive waves |
| `/api/monthly-reports` | GET | List monthly reports |
| `/api/comprehensive-waves` | GET | List comprehensive waves |
| `/api/distress-screenings` | GET | Get safeguarding alerts |
| `/api/wp6-sessions/{id}` | GET | Get WP6 sessions |
| `/api/consent/{id}` | GET | Get consent record |
| `/api/referrals` | POST | Create referral |
| `/api/nlp/responses` | GET | Get qualitative text responses (**Default limit: 2000, Max: 5000** for bulk extraction) |
| `/api/participants/{id}/nlp-responses` | GET | Get NLP responses for a specific participant |
| `/api/stats` | GET | Project statistics |
| `/api/export/records` | GET | Export all records |
| `/api/field-mapping` | GET | Current field mapping |

---

## Team Configuration

Set this in your `.env`:

```bash
REDCAP_API_URL=https://mock-redcap-service.onrender.com/api
REDCAP_API_TOKEN=mock_token_neps_2025
```

When real REDCap is ready, change only the URL and token.

## Deploy to Render (If you need to re-deploy)

1. Push this repo to GitHub
2. Connect repo to Render (New Web Service → Build and deploy from Git repository)
3. Render reads `render.yaml` and deploys automatically

