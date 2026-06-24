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

All endpoints are live on Render and can be tested directly in the browser:

| Endpoint | Method | Live Link / Example | Description |
|----------|--------|---------------------|-------------|
| `/` | GET | [Link](https://mock-redcap-service.onrender.com/) | Service info & version |
| `/health` | GET | [Link](https://mock-redcap-service.onrender.com/health) | Service health status |
| `/api/participants` | GET | [Link](https://mock-redcap-service.onrender.com/api/participants) | List participants (default limit: 100) |
| `/api/participants/{id}` | GET | [Example: NEPS-GHA-0001](https://mock-redcap-service.onrender.com/api/participants/NEPS-GHA-0001) | Get participant by ID |
| `/api/participants/{id}/monthly-reports` | GET | [Example: NEPS-GHA-0001](https://mock-redcap-service.onrender.com/api/participants/NEPS-GHA-0001/monthly-reports) | Get participant's longitudinal monthly reports |
| `/api/participants/{id}/comprehensive-waves` | GET | [Example: NEPS-GHA-0001](https://mock-redcap-service.onrender.com/api/participants/NEPS-GHA-0001/comprehensive-waves) | Get participant's comprehensive wave survey reports |
| `/api/monthly-reports` | GET | [Link](https://mock-redcap-service.onrender.com/api/monthly-reports) | List all monthly reports (default limit: 100) |
| `/api/comprehensive-waves` | GET | [Link](https://mock-redcap-service.onrender.com/api/comprehensive-waves) | List all comprehensive waves (default limit: 100) |
| `/api/distress-screenings` | GET | [Link](https://mock-redcap-service.onrender.com/api/distress-screenings) | Get safeguarding alerts & distress screenings |
| `/api/wp6-sessions/{id}` | GET | [Example: NEPS-GHA-0001](https://mock-redcap-service.onrender.com/api/wp6-sessions/NEPS-GHA-0001) | Get WP6 cognitive behavioral session logs |
| `/api/consent/{id}` | GET | [Example: NEPS-GHA-0001](https://mock-redcap-service.onrender.com/api/consent/NEPS-GHA-0001) | Get consent and assent record status |
| `/api/referrals` | POST | *Write-only endpoint* | Create a safeguarding referral |
| `/api/nlp/responses` | GET | **[Link (Full 2000-row Dataset)](https://mock-redcap-service.onrender.com/api/nlp/responses)** | Get qualitative text responses (**Default limit: 2000, Max: 5000** for bulk extraction) |
| `/api/participants/{id}/nlp-responses` | GET | [Example: NEPS-GHA-0001](https://mock-redcap-service.onrender.com/api/participants/NEPS-GHA-0001/nlp-responses) | Get NLP responses for a specific participant |
| `/api/stats` | GET | [Link](https://mock-redcap-service.onrender.com/api/stats) | Project-wide statistics (aggregate metrics) |
| `/api/export/records` | GET | [Link](https://mock-redcap-service.onrender.com/api/export/records) | Export all records in REDCap-compatible JSON format |
| `/api/field-mapping` | GET | [Link](https://mock-redcap-service.onrender.com/api/field-mapping) | Current CRF-to-internal field mapping |

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

