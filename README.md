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

## 📊 Expanded Structured Dataset (v3 Schema — Yasmine 14 + Socio-Economic)

To support ML risk-prediction model training, **Version 0.3.0** integrates a validated 150-participant × 3600-report structured dataset. The approach is **additive-only** (no rebuild, no ID drift): all pre-existing fields, IDs, and the 2000-row NLP dataset remain *completely untouched*. Only the missing fields Yasmine requested are layered in.

### What's New in v3 (0.3.0)

1. **4 New Participant-Level Socio-Economic / Demographic Fields** (12 existing → **16 fields per participant**):
   | Field | Allowed Values | Source (Yasmine Audio) |
   |-------|---------------|----------------------|
   | `employment_status` | `employed`, `unemployed`, `student`, `self-employed`, `casual_labor`, `not_applicable` | Audio 1 |
   | `food_security` | `secure`, `mildly_insecure`, `moderately_insecure`, `severely_insecure` | Audio 1 |
   | `healthcare_access` | `excellent`, `good`, `fair`, `poor`, `none` | Audio 1 |
   | `socioeconomic_status` | `high`, `upper_middle`, `middle`, `lower_middle`, `low` | Audio 1 ("General economic factors") |

2. **7 New Numeric Monthly Score Fields** (17 existing → **24 fields per monthly report**):
   | Field | Range | Derivation | Source (Yasmine 14 #) |
   |-------|-------|------------|----------------------|
   | `mood_score` | 0–30 | New, inversely correlated with depression | #2 Mood score |
   | `sleep_quality_score` | 0–30 | Numeric from `sleep_quality` categorical | #3 Sleep quality score |
   | `fatigue_score` | 0–30 | Numeric from `fatigue_level` categorical | #7 Fatigue score |
   | `attendance_score` | 0–25 | Normalized from `school_attendance_days` | #8 Attendance score |
   | `coping_score` | 0–30 | New, inversely correlated with stress | #10 Coping score |
   | `substance_abuse_score` | 0–20 | Numeric from `substance_use` categorical | #11 Substance abuse score |
   | `suicidality_score` | 0–15 | Numeric from `suicidality_screening` categorical | #12 Suicidality score |

3. **All 14 of Yasmine's Monthly Risk Parameters Are Now Present** (combination of 7 pre-existing numeric fields + 7 newly added above):
   > Stress (existed) · Mood (new) · Sleep (new) · Anxiety (existed) · Depression (existed) · Functioning (existed) · Fatigue (new) · Attendance (new) · Social isolation (existed) · Coping (new) · Substance abuse (new) · Suicidality (new) · Self-esteem (existed) · Loneliness (existed)

4. **Legacy Categorical Text Fields Preserved** — the text fields `sleep_quality`, `fatigue_level`, `substance_use`, and `suicidality_screening` are kept alongside their numeric counterparts for:
   - REDCap CRF field-mapping parity (enumerators input these as Likert categories, not numbers)
   - Clinical/human readability on the NEPS Analyst Dashboard
   - SHAP / model-explainability (explain "Poor sleep quality", not "sleep_quality_score=5.3")
   - Cross-field ETL data-quality validation (e.g., `sleep_quality=="Poor"` ⇒ `sleep_quality_score < 15`)

### Clinical Realism & Semantic Correlations
The v3 data is pre-validated with real-world effect sizes built in (r = Pearson correlations):
- Depression ↔ Anxiety: r ≈ **+0.36**
- Depression ↔ Mood score: r ≈ **−0.29** (higher depression → lower mood)
- Depression ↔ Suicidality: r ≈ **+0.24**
- Stress ↔ Coping score: r ≈ **−0.23** (higher stress → lower coping)
- Loneliness ↔ Social Isolation: r ≈ **+0.20**
- Risk flag distribution: **CRITICAL 9, HIGH 165, MEDIUM 125, LOW 3301**

### Participant ID Scheme (Locked / No Regeneration)
All 150 IDs are preserved from the prevalidated dataset — **no rebuild, no regeneration**. The 50/50/50 Ghana/Sierra Leone/Tanzania distribution uses prefixes:
- Ghana: `NEPS-GHA-0001 … NEPS-GHA-0050`
- Sierra Leone: `NEPS-SIE-0051 … NEPS-SIE-0100`
- Tanzania: `NEPS-TAN-0101 … NEPS-TAN-0150`

### How the Data Loads
At startup, the `MockDataStore` in `main.py` prefers static prevalidated JSON files with fallbacks to the original dynamic generators:
1. If `participants_updated.json` exists → load (else: dynamic generator)
2. If `monthly_reports_updated.json` exists → load flat list, convert to `{pid: [records]}` dict (else: dynamic generator)
3. `NEPS_NLP_Mock_Dataset_2000_CORRECTED.json` — loaded as before, unchanged
4. Comprehensive waves, distress screenings, WP6 sessions, consent records, and referrals **iterated over loaded participant IDs only** → guaranteed no ID drift

### v3 Seed Dataset Files (Root Directory)
Added to the repository root for the ML/AI and Data Platform teams:
1. **[participants_updated.json](file:///d:/COMPUTER_SCIENCE/NEPS-PORTAL/mock-redcap-service/participants_updated.json)** — 150 participants × 16 fields (**loaded by the API at startup**)
2. **[monthly_reports_updated.json](file:///d:/COMPUTER_SCIENCE/NEPS-PORTAL/mock-redcap-service/monthly_reports_updated.json)** — 3600 monthly reports × 24 fields (**loaded by the API at startup**)
3. **[participants_updated.csv](file:///d:/COMPUTER_SCIENCE/NEPS-PORTAL/mock-redcap-service/participants_updated.csv)** — Spreadsheet/Excel-friendly CSV copy of the above, 150 rows × 16 columns, UTF-8 BOM encoded (opens directly in Excel for country leads / analysts). Not loaded by the API.
4. **[monthly_reports_updated.csv](file:///d:/COMPUTER_SCIENCE/NEPS-PORTAL/mock-redcap-service/monthly_reports_updated.csv)** — Spreadsheet/Excel-friendly CSV copy of the above, 3600 rows × 24 columns, UTF-8 BOM encoded. Not loaded by the API.
5. **[NEPS_Mock_Data_Summary_v3.json](file:///d:/COMPUTER_SCIENCE/NEPS-PORTAL/mock-redcap-service/NEPS_Mock_Data_Summary_v3.json)** — v3 validation summary (risk distribution, semantic correlations, 14-score ranges)

> **Rule of thumb**: Keep the `.json` variants (rows 1–2) for the API and ML pipelines (they are the schema-of-record loaded at server startup). Keep the `.csv` variants (rows 3–4) for analysts opening data in Excel/Google Sheets or for Yasmine to drop straight into a pandas notebook via `pd.read_csv()`.

### Backward Compatibility Guarantees
- **All old endpoint paths unchanged** — the same API URLs/query params work as in 0.2.0
- **All old fields preserved** — no downstream code or test expecting the 0.2.0 field set breaks
- **New fields are additive in Pydantic models**, TypeScript interfaces, and ETL schemas (typed as optional in downstream consumers)
- **Dynamic generator fallbacks still exist** → reverting `main.py` without the JSON files restores 0.2.0 behavior exactly

---

## Cross-Repository Compatibility & Impact (For the Other NEPS Teams)

| Repository | Team | File Changed | Impact | Breaking? | Required Action |
|------------|------|--------------|--------|-----------|-----------------|
| **neps-portal** | Frontend | `app/types/redcap.ts` | `Participant` +4 optional fields; `SurveyResponse` +7 optional numeric score fields | **No** — all `?` | None (fields silently flow through; use in UI/dash components when ready) |
| **neps-backend** | Backend API | `app/services/redcap_mock.py` | Embedded REDCap mock: 4 socio-economic fields on participant dicts; 7 numeric ML scores on monthly responses with semantic correlations; text categoricals preserved | **No** — all existing code paths work | Set `REDCAP_MOCK_ENABLED=True` in local dev to use the richer mock |
| **neps-data-platform** | Data Eng / ETL | `etl/transform/mock_schema.py` | `demographics` instrument: +4 `FieldDefinition`s; `monthly_self_report` instrument: +7 `FieldDefinition`s | **No** — wider schema, no removals | When running `etl_pipeline.py` the normalized output tables will include the new columns |
| **mock-redcap-service** | Shared (Render deploy) | `main.py` + 3 new JSON data files | Service version bumped to `0.3.0`; static JSON loading; `get_stats()` reports `fields_added_participant=4`, `fields_added_monthly_report=7`, `schema="expanded_v3"` | **No** | Push to Render; verify `/api/stats` shows 150/3600/2000 before ML training runs |
| **ml-ai / neps-model-factory** | ML (Yasmine) | (None — consumes the Render `/api` endpoint) | The 14 risk-assessment parameters Yasmine specified are now all present as numeric columns; 4 additional socio-economic features are available for feature-engineering | **No** — purely additive inputs | Update feature selector in training scripts to include `mood_score`, `sleep_quality_score`, `fatigue_score`, `attendance_score`, `coping_score`, `substance_abuse_score`, `suicidality_score` alongside existing `stress`, `anxiety`, `depression`, `daily_functioning`, `social_isolation`, `self_esteem`, `loneliness` |

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

