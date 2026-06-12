"""
NEPS Digital — Standalone Mock REDCap API Service
=================================================
Hosted mock API for all NEPS teams. Swappable with real REDCap by changing URL.

Endpoints mirror REDCap API structure for drop-in replacement.
"""

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import random
from datetime import datetime, timedelta
import uuid
import os

app = FastAPI(
    title="NEPS Mock REDCap API",
    description="Mock REDCap API for NEPS Digital development. Returns realistic longitudinal youth mental health data for Ghana, Sierra Leone, and Tanzania.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# ─── CONFIGURATION ─────────────────────────────────────────────────

MOCK_TOKEN = os.getenv("MOCK_API_TOKEN", "mock_token_neps_2025")

# ─── INTERNAL DATA MODELS (Teams code against these) ──────────────

class Participant(BaseModel):
    participant_id: str
    country: str
    site: str
    school: str
    age: int
    date_of_birth: str
    gender: str
    grade_level: str
    enrollment_date: str
    cohort_status: str
    consent_status: str
    phone_contact: str

class MonthlyReport(BaseModel):
    participant_id: str
    month: int
    survey_date: str
    anxiety: float
    depression: float
    stress: float
    sleep_quality: str
    daily_functioning: float
    fatigue_level: str
    school_attendance_days: int
    social_isolation: float
    substance_use: str
    suicidality_screening: str
    self_esteem: float
    loneliness: float
    risk_flag: str
    requires_follow_up: bool

class ComprehensiveWave(BaseModel):
    participant_id: str
    wave_month: int
    examination_stress: float
    academic_pressure: float
    homework_burden: float
    school_climate: str
    bullying_exposure: str
    harsh_discipline: str
    educational_aspirations: str
    fear_of_failure: float
    teacher_support: float
    counselling_access: str
    household_assets: int
    food_insecurity: str
    economic_strain: float
    employment_pressure: str
    financial_stress: float
    digital_access: str
    household_instability: str
    internalised_stigma: float
    community_stigma: float
    family_stigma: float
    school_stigma: float
    mental_health_literacy: float
    help_seeking_intention: str
    help_seeking_behaviour: str
    awareness_of_services: str
    resilience_score: float
    social_support: float
    family_connectedness: float
    peer_support: float
    community_connectedness: float
    religious_support: float
    school_belonging: float

class DistressScreening(BaseModel):
    screening_id: str
    participant_id: str
    screening_date: str
    distress_score: float
    suicidality_flag: bool
    severity: str
    trigger_form: str
    trigger_item: str
    assigned_responder: str
    action_taken: str
    referral_made: bool
    referral_destination: str
    welfare_check_due: str
    resolution_status: str

class WP6Session(BaseModel):
    session_id: str
    participant_id: str
    session_number: int
    session_date: str
    attendance: str
    engagement_level: float
    fidelity_score: float
    satisfaction_score: float
    homework_completion: str
    distress_pre: float
    distress_post: float

class ConsentRecord(BaseModel):
    participant_id: str
    consent_date: str
    consent_version: str
    consent_status: str
    guardian_consent: str
    assent_status: str
    consent_withdrawn: bool
    withdrawal_reason: str
    re_consent_required: bool
    re_consent_date: Optional[str]

# ─── FIELD MAPPING (Update when real REDCap CRFs finalize) ───────

REDCAP_TO_INTERNAL = {
    "record_id": "participant_id",
    "anxiety_score": "anxiety",
    "depression_score": "depression",
    "perceived_stress_score": "stress",
    "social_isolation_score": "social_isolation",
    "self_esteem_score": "self_esteem",
    "loneliness_score": "loneliness",
    "country": "country",
    "site": "site",
    "school": "school",
    "age": "age",
    "date_of_birth": "date_of_birth",
    "gender": "gender",
    "grade_level": "grade_level",
    "enrollment_date": "enrollment_date",
    "cohort_status": "cohort_status",
    "consent_status": "consent_status",
    "phone_contact": "phone_contact",
}

INTERNAL_TO_REDCAP = {v: k for k, v in REDCAP_TO_INTERNAL.items()}

# ─── MOCK DATA STORE ──────────────────────────────────────────────

class MockDataStore:
    """Generates and stores realistic NEPS mock data."""

    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.participants = self._generate_participants()
        self.monthly_reports = self._generate_monthly_reports()
        self.comprehensive_waves = self._generate_comprehensive_waves()
        self.distress_screenings = self._generate_distress_screenings()
        self.wp6_sessions = self._generate_wp6_sessions()
        self.consent_records = self._generate_consent_records()
        self.referrals = []

    def _generate_participants(self, count: int = 150) -> List[Dict]:
        countries = {
            "Ghana": ["Kumasi", "Accra", "Ho", "Tamale"],
            "Sierra Leone": ["Freetown", "Bo", "Makeni"],
            "Tanzania": ["Dar es Salaam", "Mwanza", "Arusha"]
        }
        schools = {
            "Kumasi": ["KNUST SHS", "Prempeh College", "Opoku Ware SHS"],
            "Accra": ["Accra Academy", "Achimota School", "Presbyterian Boys"],
            "Ho": ["Mawuli School", "OLA SHS", "Sogakope SHS"],
            "Tamale": ["Tamale SHS", "Ghana SHS", "St. Charles"],
            "Freetown": ["Prince of Wales", "Methodist Boys", "Annie Walsh"],
            "Bo": ["Bo Government", "Christ the King", "St. Francis"],
            "Makeni": ["Makeni Comprehensive", "Bombali", "St. Joseph"],
            "Dar es Salaam": ["Ilboru", "Tambaza", "Kisutu"],
            "Mwanza": ["Mwanza Academy", "St. Augustine", "VETA"],
            "Arusha": ["Arusha Secondary", "Korogwe", "Moshi"]
        }

        participants = []
        for i in range(1, count + 1):
            country = random.choice(list(countries.keys()))
            site = random.choice(countries[country])
            school = random.choice(schools.get(site, ["Unknown School"]))
            age = random.randint(12, 24)
            dob = datetime.now() - timedelta(days=age*365 + random.randint(0, 364))

            participant = {
                "participant_id": f"NEPS-{country[:3].upper()}-{i:04d}",
                "country": country,
                "site": site,
                "school": school,
                "age": age,
                "date_of_birth": dob.strftime("%Y-%m-%d"),
                "gender": random.choice(["Male", "Female", "Other", "Prefer not to say"]),
                "grade_level": random.randint(7, 12) if age <= 18 else random.choice(["University", "Vocational", "Not in school"]),
                "enrollment_date": (datetime.now() - timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%d"),
                "cohort_status": random.choice(["active", "active", "active", "active", "inactive", "withdrawn"]),
                "consent_status": random.choice(["consented", "consented", "consented", "pending"]),
                "phone_contact": f"+233{random.randint(200000000, 599999999)}" if country == "Ghana" else 
                                f"+232{random.randint(30000000, 79999999)}" if country == "Sierra Leone" else 
                                f"+255{random.randint(600000000, 799999999)}",
            }
            participants.append(participant)
        return participants

    def _generate_monthly_reports(self) -> Dict[str, List[Dict]]:
        reports = {}
        for p in self.participants:
            pid = p["participant_id"]
            participant_reports = []

            # Baseline (month 0)
            baseline = self._create_monthly_report(pid, 0, is_baseline=True)
            participant_reports.append(baseline)

            # Monthly reports (1-24)
            for month in range(1, 25):
                if random.random() > 0.15:  # 85% completion
                    report = self._create_monthly_report(pid, month)
                    participant_reports.append(report)

            reports[pid] = participant_reports
        return reports

    def _create_monthly_report(self, pid: str, month: int, is_baseline: bool = False) -> Dict:
        base_stress = random.uniform(15, 35)
        trend = month * random.uniform(-0.3, 0.5)
        anxiety = round(random.uniform(0, 21), 1)
        depression = round(random.uniform(0, 27), 1)

        risk_flag = "LOW"
        requires_follow_up = False
        if anxiety > 15 or depression > 20:
            risk_flag = "HIGH"
            requires_follow_up = True

        return {
            "participant_id": pid,
            "month": month,
            "survey_date": (datetime.now() - timedelta(days=30*(24-month))).strftime("%Y-%m-%d"),
            "anxiety": anxiety,
            "depression": depression,
            "stress": round(min(40, max(0, base_stress + trend + random.uniform(-5, 5))), 1),
            "sleep_quality": random.choice(["Excellent", "Good", "Fair", "Poor"]),
            "daily_functioning": round(random.uniform(0, 100), 1),
            "fatigue_level": random.choice(["None", "Mild", "Moderate", "Severe"]),
            "school_attendance_days": random.randint(15, 22),
            "social_isolation": round(random.uniform(0, 10), 1),
            "substance_use": random.choice(["None", "Alcohol", "Cannabis", "Other"]),
            "suicidality_screening": random.choice(["No", "No", "No", "Passive thoughts", "Active plan"]),
            "self_esteem": round(random.uniform(10, 40), 1),
            "loneliness": round(random.uniform(0, 20), 1),
            "risk_flag": risk_flag,
            "requires_follow_up": requires_follow_up,
        }

    def _generate_comprehensive_waves(self) -> Dict[str, List[Dict]]:
        waves = {}
        for p in self.participants:
            pid = p["participant_id"]
            participant_waves = []
            for wave_month in [6, 12, 18, 24]:
                wave = {
                    "participant_id": pid,
                    "wave_month": wave_month,
                    "examination_stress": round(random.uniform(0, 10), 1),
                    "academic_pressure": round(random.uniform(0, 10), 1),
                    "homework_burden": round(random.uniform(0, 10), 1),
                    "school_climate": random.choice(["Supportive", "Neutral", "Hostile"]),
                    "bullying_exposure": random.choice(["None", "Verbal", "Physical", "Cyber", "Multiple"]),
                    "harsh_discipline": random.choice(["Never", "Rarely", "Sometimes", "Often"]),
                    "educational_aspirations": random.choice(["University", "Vocational", "Employment", "Undecided"]),
                    "fear_of_failure": round(random.uniform(0, 10), 1),
                    "teacher_support": round(random.uniform(0, 10), 1),
                    "counselling_access": random.choice(["Yes", "No", "Don't know"]),
                    "household_assets": random.randint(0, 20),
                    "food_insecurity": random.choice(["None", "Mild", "Moderate", "Severe"]),
                    "economic_strain": round(random.uniform(0, 10), 1),
                    "employment_pressure": random.choice(["None", "Family expects", "Self pressure", "Financial need"]),
                    "financial_stress": round(random.uniform(0, 10), 1),
                    "digital_access": random.choice(["Smartphone", "Basic phone", "Shared", "None"]),
                    "household_instability": random.choice(["Stable", "Some instability", "Highly unstable"]),
                    "internalised_stigma": round(random.uniform(0, 10), 1),
                    "community_stigma": round(random.uniform(0, 10), 1),
                    "family_stigma": round(random.uniform(0, 10), 1),
                    "school_stigma": round(random.uniform(0, 10), 1),
                    "mental_health_literacy": round(random.uniform(0, 20), 1),
                    "help_seeking_intention": random.choice(["Yes", "Maybe", "No"]),
                    "help_seeking_behaviour": random.choice(["Professional", "Informal", "Religious", "None"]),
                    "awareness_of_services": random.choice(["Good", "Some", "None"]),
                    "resilience_score": round(random.uniform(0, 100), 1),
                    "social_support": round(random.uniform(0, 20), 1),
                    "family_connectedness": round(random.uniform(0, 20), 1),
                    "peer_support": round(random.uniform(0, 20), 1),
                    "community_connectedness": round(random.uniform(0, 20), 1),
                    "religious_support": round(random.uniform(0, 20), 1),
                    "school_belonging": round(random.uniform(0, 20), 1),
                }
                participant_waves.append(wave)
            waves[pid] = participant_waves
        return waves

    def _generate_distress_screenings(self) -> List[Dict]:
        screenings = []
        for p in self.participants:
            if random.random() > 0.9:  # 10% flagged
                screening = {
                    "screening_id": f"SCR-{uuid.uuid4().hex[:8].upper()}",
                    "participant_id": p["participant_id"],
                    "screening_date": datetime.now().strftime("%Y-%m-%d"),
                    "distress_score": round(random.uniform(15, 30), 1),
                    "suicidality_flag": random.choice([True, True, False]),
                    "severity": random.choice(["high", "critical"]),
                    "trigger_form": "monthly_self_report",
                    "trigger_item": "suicidality_screening",
                    "assigned_responder": random.choice(["Dr. Otu-Ansah", "Counselor A", "Counselor B"]),
                    "action_taken": "",
                    "referral_made": False,
                    "referral_destination": "",
                    "welfare_check_due": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
                    "resolution_status": "open",
                }
                screenings.append(screening)
        return screenings

    def _generate_wp6_sessions(self) -> Dict[str, List[Dict]]:
        sessions = {}
        for p in self.participants[:20]:  # 20 participants enrolled
            pid = p["participant_id"]
            participant_sessions = []
            for session_num in range(1, 9):
                session = {
                    "session_id": f"SES-{uuid.uuid4().hex[:8].upper()}",
                    "participant_id": pid,
                    "session_number": session_num,
                    "session_date": (datetime.now() - timedelta(days=30*(8-session_num))).strftime("%Y-%m-%d"),
                    "attendance": random.choice(["Present", "Present", "Present", "Absent", "Partial"]),
                    "engagement_level": round(random.uniform(1, 5), 1),
                    "fidelity_score": round(random.uniform(70, 100), 1),
                    "satisfaction_score": round(random.uniform(3, 5), 1),
                    "homework_completion": random.choice(["Complete", "Partial", "None"]),
                    "distress_pre": round(random.uniform(10, 25), 1),
                    "distress_post": round(random.uniform(5, 15), 1),
                }
                participant_sessions.append(session)
            sessions[pid] = participant_sessions
        return sessions

    def _generate_consent_records(self) -> List[Dict]:
        records = []
        for p in self.participants:
            records.append({
                "participant_id": p["participant_id"],
                "consent_date": p["enrollment_date"],
                "consent_version": "v1.0",
                "consent_status": p["consent_status"],
                "guardian_consent": random.choice(["Yes", "Yes", "Yes", "N/A (18+)"]),
                "assent_status": random.choice(["Yes", "Yes", "Yes", "Pending"]),
                "consent_withdrawn": False,
                "withdrawal_reason": "",
                "re_consent_required": random.choice([False, False, False, True]),
                "re_consent_date": None,
            })
        return records

    # ─── PUBLIC METHODS ─────────────────────────────────────────────

    def get_participants(self, country: Optional[str] = None, 
                        site: Optional[str] = None,
                        status: Optional[str] = None) -> List[Dict]:
        results = self.participants.copy()
        if country:
            results = [p for p in results if p["country"] == country]
        if site:
            results = [p for p in results if p["site"] == site]
        if status:
            results = [p for p in results if p["cohort_status"] == status]
        return results

    def get_participant(self, participant_id: str) -> Optional[Dict]:
        return next((p for p in self.participants if p["participant_id"] == participant_id), None)

    def get_monthly_reports(self, participant_id: Optional[str] = None) -> List[Dict]:
        if participant_id:
            return self.monthly_reports.get(participant_id, [])
        return [r for reports in self.monthly_reports.values() for r in reports]

    def get_comprehensive_waves(self, participant_id: Optional[str] = None) -> List[Dict]:
        if participant_id:
            return self.comprehensive_waves.get(participant_id, [])
        return [w for waves in self.comprehensive_waves.values() for w in waves]

    def get_distress_screenings(self, status: Optional[str] = None) -> List[Dict]:
        if status:
            return [s for s in self.distress_screenings if s["resolution_status"] == status]
        return self.distress_screenings

    def get_wp6_sessions(self, participant_id: str) -> List[Dict]:
        return self.wp6_sessions.get(participant_id, [])

    def get_consent_record(self, participant_id: str) -> Optional[Dict]:
        return next((c for c in self.consent_records if c["participant_id"] == participant_id), None)

    def create_referral(self, participant_id: str, destination: str, notes: str = "") -> Dict:
        referral = {
            "referral_id": f"REF-{uuid.uuid4().hex[:8].upper()}",
            "participant_id": participant_id,
            "initiation_date": datetime.now().strftime("%Y-%m-%d"),
            "destination": destination,
            "status": "initiated",
            "notes": notes,
            "follow_up_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        }
        self.referrals.append(referral)
        return referral

    def get_stats(self) -> Dict:
        return {
            "total_participants": len(self.participants),
            "by_country": {
                "Ghana": len([p for p in self.participants if p["country"] == "Ghana"]),
                "Sierra Leone": len([p for p in self.participants if p["country"] == "Sierra Leone"]),
                "Tanzania": len([p for p in self.participants if p["country"] == "Tanzania"]),
            },
            "active_cohort": len([p for p in self.participants if p["cohort_status"] == "active"]),
            "total_monthly_reports": sum(len(r) for r in self.monthly_reports.values()),
            "total_waves": sum(len(w) for w in self.comprehensive_waves.values()),
            "high_risk_flags": len(self.distress_screenings),
            "open_referrals": len([r for r in self.referrals if r["status"] == "initiated"]),
            "wp6_enrolled": len(self.wp6_sessions),
            "source": "mock",
            "version": "0.1.0"
        }

# Initialize store
store = MockDataStore()

# ─── API ENDPOINTS ────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "service": "NEPS Mock REDCap API",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "participants": "/api/participants",
            "monthly_reports": "/api/monthly-reports",
            "comprehensive_waves": "/api/comprehensive-waves",
            "distress_screenings": "/api/distress-screenings",
            "wp6_sessions": "/api/wp6-sessions",
            "consent": "/api/consent",
            "referrals": "/api/referrals",
            "stats": "/api/stats",
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "neps-mock-api", "source": "mock"}

@app.get("/api/participants")
def list_participants(
    country: Optional[str] = None,
    site: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500)
):
    """Get participant registry with filtering."""
    data = store.get_participants(country=country, site=site, status=status)
    return {
        "data": data[:limit],
        "total": len(data),
        "source": "mock"
    }

@app.get("/api/participants/{participant_id}")
def get_participant(participant_id: str):
    """Get single participant by ID."""
    participant = store.get_participant(participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    return participant

@app.get("/api/participants/{participant_id}/monthly-reports")
def get_participant_monthly_reports(participant_id: str):
    """Get monthly self-reports for a participant."""
    reports = store.get_monthly_reports(participant_id=participant_id)
    return {
        "participant_id": participant_id,
        "reports": reports,
        "count": len(reports)
    }

@app.get("/api/participants/{participant_id}/comprehensive-waves")
def get_participant_waves(participant_id: str):
    """Get comprehensive survey waves for a participant."""
    waves = store.get_comprehensive_waves(participant_id=participant_id)
    return {
        "participant_id": participant_id,
        "waves": waves,
        "count": len(waves)
    }

@app.get("/api/monthly-reports")
def list_monthly_reports(
    country: Optional[str] = None,
    risk_flag: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all monthly reports with filtering."""
    reports = store.get_monthly_reports()

    if country:
        # Filter by participant country
        participant_ids = {p["participant_id"] for p in store.get_participants(country=country)}
        reports = [r for r in reports if r["participant_id"] in participant_ids]

    if risk_flag:
        reports = [r for r in reports if r["risk_flag"] == risk_flag]

    return {
        "data": reports[:limit],
        "total": len(reports),
        "source": "mock"
    }

@app.get("/api/comprehensive-waves")
def list_comprehensive_waves(
    wave_month: Optional[int] = None,
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all comprehensive waves with filtering."""
    waves = store.get_comprehensive_waves()

    if wave_month:
        waves = [w for w in waves if w["wave_month"] == wave_month]

    return {
        "data": waves[:limit],
        "total": len(waves),
        "source": "mock"
    }

@app.get("/api/distress-screenings")
def list_distress_screenings(status: Optional[str] = None):
    """Get distress/safeguarding screenings."""
    screenings = store.get_distress_screenings(status=status)
    return {
        "screenings": screenings,
        "count": len(screenings),
        "high_risk_count": len([s for s in screenings if s["severity"] in ["high", "critical"]]),
        "source": "mock"
    }

@app.get("/api/wp6-sessions/{participant_id}")
def get_wp6_sessions(participant_id: str):
    """Get WP6 intervention sessions for a participant."""
    sessions = store.get_wp6_sessions(participant_id)
    return {
        "participant_id": participant_id,
        "sessions": sessions,
        "total_sessions": len(sessions),
        "attendance_rate": round(len([s for s in sessions if s["attendance"] == "Present"]) / len(sessions) * 100, 1) if sessions else 0
    }

@app.get("/api/consent/{participant_id}")
def get_consent(participant_id: str):
    """Get consent record for a participant."""
    consent = store.get_consent_record(participant_id)
    if not consent:
        raise HTTPException(status_code=404, detail="Consent record not found")
    return consent

@app.post("/api/referrals")
def create_referral_endpoint(
    participant_id: str,
    destination: str,
    notes: str = ""
):
    """Create a safeguarding referral."""
    referral = store.create_referral(participant_id, destination, notes)
    return referral

@app.get("/api/stats")
def get_stats():
    """Get project statistics."""
    return store.get_stats()

@app.get("/api/export/records")
def export_records(
    format: str = Query("json", regex="^(json|csv)$"),
    instrument: Optional[str] = Query(None, regex="^(monthly|comprehensive|all)$")
):
    """Export records in REDCap-compatible format."""
    records = []

    if instrument in ["monthly", "all"]:
        records.extend(store.get_monthly_reports())
    if instrument in ["comprehensive", "all"]:
        records.extend(store.get_comprehensive_waves())
    if not instrument:
        records.extend(store.get_monthly_reports())

    if format == "csv":
        import csv
        import io
        output = io.StringIO()
        if records:
            writer = csv.DictWriter(output, fieldnames=records[0].keys())
            writer.writeheader()
            writer.writerows(records)
        return {"data": output.getvalue(), "format": "csv"}

    return {"data": records, "format": "json", "count": len(records)}

@app.get("/api/field-mapping")
def get_field_mapping():
    """Get current field mapping (for CRF alignment)."""
    return {
        "redcap_to_internal": REDCAP_TO_INTERNAL,
        "internal_to_redcap": INTERNAL_TO_REDCAP,
        "note": "Update this mapping when real REDCap CRFs are finalized"
    }
