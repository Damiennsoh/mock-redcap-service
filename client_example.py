"""
NEPS Digital — REDCap API Client Example
=========================================
Use this in your service (backend, data-platform, ml-ai) to connect to mock or real REDCap.
"""

import os
import requests
from typing import Optional, List, Dict

# Configuration — change these when real REDCap is ready
REDCAP_API_URL = os.getenv("REDCAP_API_URL", "https://your-render-url.onrender.com/api")
REDCAP_API_TOKEN = os.getenv("REDCAP_API_TOKEN", "mock_token_neps_2025")


class RedCapClient:
    """Client for REDCap API. Works with mock (dev) and real (prod)."""

    def __init__(self, base_url: str = REDCAP_API_URL, token: str = REDCAP_API_TOKEN):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {token}"}

    def _get(self, endpoint: str, params: dict = None) -> dict:
        """Make GET request."""
        response = requests.get(f"{self.base_url}{endpoint}", params=params, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint: str, data: dict = None) -> dict:
        """Make POST request."""
        response = requests.post(f"{self.base_url}{endpoint}", json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

    # ─── PARTICIPANTS ──────────────────────────────────────────────

    def get_participants(self, country: Optional[str] = None) -> List[Dict]:
        """Get participant registry."""
        params = {"country": country} if country else {}
        return self._get("/participants", params).get("data", [])

    def get_participant(self, participant_id: str) -> Dict:
        """Get single participant."""
        return self._get(f"/participants/{participant_id}")

    # ─── SURVEYS ───────────────────────────────────────────────────

    def get_monthly_reports(self, participant_id: Optional[str] = None) -> List[Dict]:
        """Get monthly self-reports."""
        if participant_id:
            return self._get(f"/participants/{participant_id}/monthly-reports").get("reports", [])
        return self._get("/monthly-reports").get("data", [])

    def get_comprehensive_waves(self, participant_id: Optional[str] = None) -> List[Dict]:
        """Get comprehensive survey waves."""
        if participant_id:
            return self._get(f"/participants/{participant_id}/comprehensive-waves").get("waves", [])
        return self._get("/comprehensive-waves").get("data", [])

    # ─── SAFEGUARDING ──────────────────────────────────────────────

    def get_distress_screenings(self, status: Optional[str] = None) -> List[Dict]:
        """Get distress/safeguarding screenings."""
        params = {"status": status} if status else {}
        return self._get("/distress-screenings", params).get("screenings", [])

    def create_referral(self, participant_id: str, destination: str, notes: str = "") -> Dict:
        """Create safeguarding referral."""
        return self._post("/referrals", {
            "participant_id": participant_id,
            "destination": destination,
            "notes": notes
        })

    # ─── WP6 ───────────────────────────────────────────────────────

    def get_wp6_sessions(self, participant_id: str) -> List[Dict]:
        """Get WP6 intervention sessions."""
        return self._get(f"/wp6-sessions/{participant_id}").get("sessions", [])

    # ─── CONSENT ─────────────────────────────────────────────────────

    def get_consent(self, participant_id: str) -> Dict:
        """Get consent record."""
        return self._get(f"/consent/{participant_id}")

    # ─── EXPORT ────────────────────────────────────────────────────

    def export_records(self, instrument: str = "all") -> List[Dict]:
        """Export all records."""
        return self._get("/export/records", {"instrument": instrument}).get("data", [])

    def get_stats(self) -> Dict:
        """Get project statistics."""
        return self._get("/stats")

    def get_field_mapping(self) -> Dict:
        """Get current field mapping."""
        return self._get("/field-mapping")


# Example usage
if __name__ == "__main__":
    client = RedCapClient()

    # Test connection
    stats = client.get_stats()
    print(f"Connected: {stats['total_participants']} participants")

    # Get Ghana participants
    ghana = client.get_participants(country="Ghana")
    print(f"Ghana: {len(ghana)} participants")

    # Get monthly reports
    reports = client.get_monthly_reports()
    print(f"Total monthly reports: {len(reports)}")
