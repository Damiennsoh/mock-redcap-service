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
    version="0.2.0",
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

class NLPResponse(BaseModel):
    participant_id: str
    response_id: str
    response_type: str
    collection_date: str
    month: Optional[str] = None
    country: str
    site: str
    question_prompt: str
    response_text: str
    word_count: int
    language: str
    translated: Optional[bool] = False
    severity_level: str
    anxiety_level: str
    depression_level: str
    stress_level: str
    emotional_label: str
    clinical_status: str
    suicidality_flag: str
    requires_referral: str
    alert_priority: str
    thematic_codes: List[str]
    sentiment_manual: str
    sentiment_score: float

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
        # Load pre-generated 2000-row semantically correlated dataset if available, otherwise fall back to generator
        import json
        json_path = os.path.join(os.path.dirname(__file__), "NEPS_NLP_Mock_Dataset_2000_v2.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    self.nlp_responses = json.load(f)
            except Exception as e:
                print(f"Error loading NEPS_NLP_Mock_Dataset_2000_v2.json: {e}. Falling back to generator.")
                self.nlp_responses = self._generate_nlp_data()
        else:
            self.nlp_responses = self._generate_nlp_data()
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

    # ─── TEXT ANALYSIS HELPERS ───────────────────────────────────────

    @staticmethod
    def _analyze_text(text: str) -> Dict:
        """
        Derive all NLP labels from the actual text content using a rule-based scorer.
        Every label is deterministically computed from word patterns — no random assignment.
        This ensures the ML training data contains real text-to-label correlations.
        """
        text_lower = text.lower()

        # --- Word banks ---
        positive_words = [
            "fine", "okay", "good", "happy", "hopeful", "enjoy", "supportive",
            "relax", "well", "manage", "handle", "great", "love", "grateful",
            "peaceful", "calm", "motivated", "confident",
        ]
        negative_words = [
            "stress", "anxious", "worried", "alone", "overwhelmed", "cry", "sad",
            "tired", "struggle", "pressure", "hard", "uneasy", "falling behind",
            "can't focus", "compare", "hide", "argue",
        ]
        crisis_words = [
            "give up", "disappear", "invisible", "darkness", "hurting",
            "meaningless", "burden", "no point", "can't hold on", "suicide",
            "no way out", "hopeless", "emptiness", "pain inside",
        ]
        anxiety_words = [
            "anxious", "nervous", "worry", "panic", "can't sleep", "racing",
            "overwhelmed", "uneasy", "pressure",
        ]
        depression_words = [
            "sad", "empty", "hopeless", "cry", "tired", "meaningless",
            "no point", "burden", "darkness", "exhausting", "emptiness",
        ]

        # --- Score word counts ---
        pos_count = sum(1 for w in positive_words if w in text_lower)
        neg_count = sum(1 for w in negative_words if w in text_lower)
        crisis_count = sum(1 for w in crisis_words if w in text_lower)
        anxiety_count = sum(1 for w in anxiety_words if w in text_lower)
        depression_count = sum(1 for w in depression_words if w in text_lower)

        # --- Sentiment score: -1.0 to +1.0 ---
        total_emotion_words = pos_count + neg_count + crisis_count + 1  # +1 avoids div/0
        raw_sentiment = (pos_count - neg_count - (crisis_count * 2)) / total_emotion_words
        sentiment_score = round(max(-1.0, min(1.0, raw_sentiment)), 2)

        # --- Severity: derived from sentiment + crisis words ---
        if crisis_count >= 2 or sentiment_score < -0.6:
            severity = "high"
        elif neg_count >= 2 or sentiment_score < -0.2:
            severity = "moderate"
        else:
            severity = "low"

        # --- Emotional label: derived from dominant word pattern ---
        if crisis_count > 0:
            emotion = "sadness"
        elif neg_count > pos_count:
            if anxiety_count >= 1:
                emotion = "fear"
            elif depression_count >= 1:
                emotion = "sadness"
            else:
                emotion = "disappointment"
        elif pos_count > neg_count:
            if any(w in text_lower for w in ["happy", "enjoy", "love"]):
                emotion = "joy"
            else:
                emotion = "hope"
        else:
            emotion = "confusion"

        # --- Clinical status: derived from severity + specific word patterns ---
        if crisis_count >= 2:
            clinical = "suicidal_ideation"
        elif crisis_count == 1 or depression_count >= 3:
            clinical = "depressed"
        elif anxiety_count >= 2:
            clinical = "anxious"
        elif neg_count >= 2:
            clinical = "stressed"
        else:
            clinical = "normal"

        # --- Sub-scores: derived from word counts ---
        anxiety_level = "high" if anxiety_count >= 2 else ("moderate" if anxiety_count == 1 else "low")
        depression_level = "high" if depression_count >= 2 else ("moderate" if depression_count == 1 else "low")
        stress_level = "high" if any(w in text_lower for w in ["stress", "overwhelmed", "pressure"]) else "low"

        # --- Sentiment manual label (5-tier classification) ---
        if sentiment_score >= 0.5:
            sentiment_manual = "positive"
        elif sentiment_score >= 0.1:
            sentiment_manual = "mildly_positive"
        elif sentiment_score >= -0.1:
            sentiment_manual = "neutral"
        elif sentiment_score > -0.5:
            sentiment_manual = "mildly_negative"
        else:
            sentiment_manual = "negative"

        return {
            "sentiment_score": sentiment_score,
            "sentiment_manual": sentiment_manual,
            "severity_level": severity,
            "emotional_label": emotion,
            "clinical_status": clinical,
            "anxiety_level": anxiety_level,
            "depression_level": depression_level,
            "stress_level": stress_level,
            "suicidality_flag": "yes" if crisis_count >= 2 else "no",
            "requires_referral": "yes" if severity == "high" or clinical == "suicidal_ideation" else "no",
            "alert_priority": "p0" if clinical == "suicidal_ideation" else ("p1" if severity == "high" else "p2"),
        }

    @staticmethod
    def _derive_themes(text: str) -> List[str]:
        """Extract thematic codes from text content — no random sampling."""
        themes = []
        text_lower = text.lower()
        if any(w in text_lower for w in ["school", "exam", "teacher", "class", "homework", "workload"]):
            themes.append("academic_pressure")
        if any(w in text_lower for w in ["family", "parent", "mother", "father", "home"]):
            themes.append("family_conflict")
        if any(w in text_lower for w in ["money", "financial", "afford", "poor"]):
            themes.append("financial_stress")
        if any(w in text_lower for w in ["friend", "alone", "lonely", "isolated", "social"]):
            themes.append("social_isolation")
        if any(w in text_lower for w in ["sleep", "tired", "exhausted", "health", "hurt"]):
            themes.append("health_concerns")
        if any(w in text_lower for w in ["dark", "pain", "give up", "meaningless", "no point", "disappear"]):
            themes.append("crisis_indicators")
        return themes or ["general_distress"]

    def _generate_nlp_data(self, count: int = 500) -> List[Dict]:
        """
        Generate qualitative text responses for ML training.

        IMPORTANT: Every label (sentiment_score, emotional_label, severity_level,
        clinical_status, anxiety_level, depression_level, stress_level) is derived
        directly from the response_text using _analyze_text(). No random label
        assignment — the model will learn real text-to-label correlations.
        """
        # Templates crafted to produce specific, predictable label profiles.
        # Each has enough signal words to yield deterministic scores from _analyze_text().
        templates = [
            # ── LOW severity / POSITIVE sentiment ──────────────────────────────
            "School is fine, I manage my work okay. My friends are supportive and I feel hopeful about finishing this year.",
            "I enjoy spending time with my family on weekends. Playing football helps me relax and I sleep well most nights.",
            "My teachers are helpful when I ask questions. I had a good day today, nothing special happened.",
            "I feel okay about school. The workload is manageable and I feel good when I finish my assignments.",
            "Things are going well. I am grateful for my supportive family and I feel hopeful about the future.",
            "I sleep well and I manage my daily tasks okay. My friends keep me motivated and I feel calm.",
            "Life is good right now. I enjoy my studies and I feel confident about my upcoming exams.",
            "I had a great week. My family was supportive and I feel grateful for what I have.",

            # ── MODERATE severity / MIXED sentiment ────────────────────────────
            "School is very stressful. Exams make me anxious and I can't sleep well at night.",
            "I feel alone sometimes. My friends don't fully understand me and I worry about my situation.",
            "The workload feels too much. I feel overwhelmed by everything expected of me at school.",
            "I worry about my family's money and it affects my concentration. Sometimes I cry but I hide it.",
            "I feel overwhelmed and I struggle to focus. The pressure from school is too much right now.",
            "Sometimes I cry at night because I feel alone and sad. I hide it from my friends and family.",
            "My parents argue a lot and it makes me feel uneasy and anxious. I struggle to sleep well.",
            "I feel like I'm falling behind and can't catch up. The stress is making me anxious and tired.",
            "Social media makes me compare myself to others constantly. I feel sad and overwhelmed by it.",
            "I feel alone and worried most days. The academic pressure is too much and I can't sleep.",

            # ── HIGH severity / CRISIS ─────────────────────────────────────────
            "Sometimes I think about giving up. Life feels too hard to continue and the darkness is overwhelming.",
            "I can't sleep anymore. My mind races with dark thoughts every night. I see no way out.",
            "Nobody would notice if I disappeared. I feel completely invisible and there is no point anymore.",
            "The pressure is crushing me. I see no way out of this darkness. I feel like a burden to everyone.",
            "I've started hurting myself to feel something. I don't see the point in anything, everything is meaningless.",
            "I don't see the point in anything anymore. Everything feels meaningless and I feel empty inside.",
            "Every day feels the same — hopeless and exhausting. I feel like a burden to my family and friends.",
            "The pain inside is too much. I don't know how much longer I can hold on. I feel completely invisible.",
            "I feel like giving up. The darkness is too heavy. I can't hold on much longer. There is no point.",
            "Life feels meaningless and I see no way out. I feel like a burden and want to disappear.",
        ]

        variations = [
            " Today was especially difficult.",
            " I don't know who to talk to.",
            " This has been going on for months.",
            " I wish things were different.",
            "",  # No variation
        ]

        question_prompts = [
            "Tell us about your biggest challenge right now",
            "How do you cope with stress in your daily life?",
            "What support do you need that you are not receiving?",
            "Describe your school experience this term",
            "How do you feel about your future after school?",
            "What makes you feel happy or hopeful?",
            "Describe a time when you felt really low",
            "What would you change about your current situation?",
            "How do you feel about your relationships with family?",
            "What are your thoughts about your mental health?",
        ]

        response_types = ["youth_narrative", "interview_transcript", "open_ended", "journal_entry"]
        countries = ["GHA", "SLE", "TZA"]
        sites = {
            "GHA": ["KNUST", "Accra_Poly", "Tamale_Tech"],
            "SLE": ["Fourah_Bay", "Eastern_Tech", "Bo_Campus"],
            "TZA": ["UDSM", "Ardhi", "MUST"],
        }

        nlp_data = []
        for _ in range(count):
            base_text = random.choice(templates)
            text = base_text + random.choice(variations)
            country = random.choice(countries)
            site = random.choice(sites[country])

            # ALL labels derived from text content — not randomly assigned
            analysis = self._analyze_text(text)
            themes = self._derive_themes(text)

            date_obj = datetime.now() - timedelta(days=random.randint(1, 180))
            collection_date = date_obj.strftime("%Y-%m-%d")
            month_name = date_obj.strftime("%B")

            nlp_data.append({
                "participant_id": f"NEPS-{country}-{random.randint(1, 150):04d}",
                "response_id": f"NLP-{uuid.uuid4().hex[:8].upper()}",
                "response_type": random.choice(response_types),
                "collection_date": collection_date,
                "month": month_name,
                "country": country,
                "site": site,
                "question_prompt": random.choice(question_prompts),
                "response_text": text,
                "word_count": len(text.split()),
                "language": "en",
                "translated": False,
                # ── Labels derived from text, not random ──
                "severity_level": analysis["severity_level"],
                "anxiety_level": analysis["anxiety_level"],
                "depression_level": analysis["depression_level"],
                "stress_level": analysis["stress_level"],
                "emotional_label": analysis["emotional_label"],
                "clinical_status": analysis["clinical_status"],
                "sentiment_score": analysis["sentiment_score"],
                "sentiment_manual": analysis["sentiment_manual"],
                "suicidality_flag": analysis["suicidality_flag"],
                "requires_referral": analysis["requires_referral"],
                "alert_priority": analysis["alert_priority"],
                "thematic_codes": themes,
            })

        return nlp_data

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

    def get_nlp_responses(
        self,
        response_type: Optional[str] = None,
        sentiment: Optional[str] = None,
        severity: Optional[str] = None,
        clinical_status: Optional[str] = None,
        emotional_label: Optional[str] = None,
    ) -> List[Dict]:
        results = self.nlp_responses.copy()
        if response_type:
            results = [r for r in results if r["response_type"] == response_type]
        if sentiment:
            results = [r for r in results if r["sentiment_manual"] == sentiment]
        if severity:
            results = [r for r in results if r["severity_level"] == severity]
        if clinical_status:
            results = [r for r in results if r["clinical_status"] == clinical_status]
        if emotional_label:
            results = [r for r in results if r["emotional_label"] == emotional_label]
        return results

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
            "nlp_responses_count": len(self.nlp_responses),
            "source": "mock",
            "version": "0.2.0"
        }

# Initialize store
store = MockDataStore()

# ─── API ENDPOINTS ────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "service": "NEPS Mock REDCap API",
        "version": "0.2.0",
        "docs": "/docs",
        "endpoints": {
            "participants": "/api/participants",
            "monthly_reports": "/api/monthly-reports",
            "comprehensive_waves": "/api/comprehensive-waves",
            "distress_screenings": "/api/distress-screenings",
            "wp6_sessions": "/api/wp6-sessions",
            "consent": "/api/consent",
            "referrals": "/api/referrals",
            "nlp_responses": "/api/nlp/responses",
            "stats": "/api/stats",
        }
    }

@app.get("/api/nlp/responses")
def list_nlp_responses(
    limit: int = Query(2000, ge=1, le=5000),
    severity: Optional[str] = Query(None, regex="^(low|moderate|high)$"),
    clinical_status: Optional[str] = None,
    emotional_label: Optional[str] = None,
    response_type: Optional[str] = None,
    sentiment: Optional[str] = None,
):
    """Get qualitative text responses for NLP/ML training."""
    data = store.get_nlp_responses(
        response_type=response_type,
        sentiment=sentiment,
        severity=severity,
        clinical_status=clinical_status,
        emotional_label=emotional_label,
    )
    filtered = data[:limit]
    return {
        "count": len(filtered),
        "filters_applied": {
            "severity": severity,
            "clinical_status": clinical_status,
            "emotional_label": emotional_label,
            "response_type": response_type,
            "sentiment": sentiment,
        },
        "data": filtered,
        "source": "mock"
    }

@app.get("/api/participants/{participant_id}/nlp-responses")
def get_participant_nlp_responses(participant_id: str):
    """Get NLP responses for a specific participant."""
    participant = store.get_participant(participant_id)
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")
    responses = [r for r in store.nlp_responses if r["participant_id"] == participant_id]
    return {
        "participant_id": participant_id,
        "responses": responses,
        "count": len(responses)
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
