# NEPS Mock REDCap API

Standalone mock REDCap API service for NEPS Digital development. It provides realistic longitudinal youth mental health data for Ghana, Sierra Leone, and Tanzania.

## Deployed Service

The mock API is currently deployed on Render!
- **URL**: https://mock-redcap-service.onrender.com
- **API Base Path**: https://mock-redcap-service.onrender.com/api
- **Docs**: https://mock-redcap-service.onrender.com/docs
- **Health Check**: https://mock-redcap-service.onrender.com/health

## 🧠 Semantically Correlated NLP Dataset (v2)

To resolve issues with random label noise in ML training, an upgraded **2000-row semantically correlated NLP dataset (v2)** has been integrated directly into the service. 

### What's New in v2
1. **Restored `sentiment_manual` & `month` columns**: The dataset now contains exactly **23 columns** matching the full production schema.
2. **Deterministic Text-to-Label Derivation**: Every single label is computed directly from the words inside the `response_text` — zero random noise.
3. **5-Tier Sentiment Classification**: The `sentiment_manual` field is mapped according to the following rules:
   * **`positive`** (sentiment_score $\ge 0.5$): *e.g., "I feel proud of myself. My family celebrated with me."*
   * **`mildly_positive`** (0.1 to 0.49): *e.g., "I trust my judgment and problem-solving skills."*
   * **`neutral`** (-0.1 to 0.1): *e.g., "I feel calm and in control of my space."*
   * **`mildly_negative`** (-0.49 to -0.11): *e.g., "I feel disappointed in myself."*
   * **`negative`** (sentiment_score $\le -0.5$): *e.g., "Life feels too hard to continue. Nobody would notice if I disappeared."*

### Restored 23-Column Schema
```csv
participant_id, response_id, response_type, collection_date, month, country, site,
question_prompt, response_text, word_count, language, severity_level, anxiety_level,
depression_level, stress_level, emotional_label, clinical_status, sentiment_score,
sentiment_manual, suicidality_flag, requires_referral, alert_priority, thematic_codes
```

### Key Fixes Implemented (v3 CORRECTED)
Based on feedback from the ML/AI teams, the dataset has been fully corrected and validated:
- **Ground-Truth Label Pre-Assignment**: Labels are now assigned *before* text generation rather than analyzed after, guaranteeing 100% accurate text-to-label semantic correlation.
- **Natural Emotional Expression**: Text narratives are explicitly crafted to naturally and realistically express the pre-assigned emotions.
- **Zero Duplicates**: Synonym substitution and variation phrases ensure there are exactly zero duplicate narratives in the 2000 records.
- **Comprehensive Sentiment Calibration**: `sentiment_score` values are randomized within the correct mathematical range for each of the 5 `sentiment_manual` tiers.

### Seed Dataset Files (Root Directory)
The repository contains the following verified files for the ML/AI and Data Platform teams:
1. **[NEPS_NLP_Mock_Dataset_2000_CORRECTED.json](file:///d:/COMPUTER_SCIENCE/NEPS-PORTAL/mock-redcap-service/NEPS_NLP_Mock_Dataset_2000_CORRECTED.json)**: The full, corrected 2000-record dataset in JSON format. Loaded directly by the API at startup.
2. **[NEPS_NLP_Mock_Dataset_2000_CORRECTED.csv](file:///d:/COMPUTER_SCIENCE/NEPS-PORTAL/mock-redcap-service/NEPS_NLP_Mock_Dataset_2000_CORRECTED.csv)**: Spreadsheet-friendly CSV version of the corrected dataset.
3. **[NEPS_NLP_Validation_Report.json](file:///d:/COMPUTER_SCIENCE/NEPS-PORTAL/mock-redcap-service/NEPS_NLP_Validation_Report.json)**: Validation report detailing final distributions (23 columns, 15+ emotions, 15+ themes, zero duplicates, exact correlation proof).
4. **[NEPS_NLP_Dataset_Summary.json](file:///d:/COMPUTER_SCIENCE/NEPS-PORTAL/mock-redcap-service/NEPS_NLP_Dataset_Summary.json)**: High-level dataset summary.

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

