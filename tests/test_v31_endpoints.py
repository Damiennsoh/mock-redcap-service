"""
Tests for mock-redcap-service V3.1 Endpoints
============================================
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_v31_dictionary_endpoint():
    response = client.get("/api/v31/dictionary")
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["total_fields"] == 223
    assert len(data["data"]) == 223
    assert data["metadata"]["version"] == "3.1"


def test_v31_baseline_get_endpoint():
    response = client.get("/api/v31/baseline")
    assert response.status_code == 200
    data = response.json()
    assert len(data["data"]) >= 150
    assert data["metadata"]["track"] == "v31_baseline"


def test_v31_baseline_post_submission():
    payload = {
        "country": "1",
        "site_id": "KNUST_TEST",
        "site_setting": "1",
        "age_years": 17,
        "sex_report": "2",
        "contact_24m": "1",
        "willing_24m": "1",
        "esi_finstrain_1": 2,
        "esi_finstrain_2": 2,
        "esi_food_1": 1,
        "esi_food_2": 1,
        "esi_educost_1": 2,
        "esi_educost_2": 2,
        "esi_materials_1": 2,
        "esi_materials_2": 2,
        "esi_transport_1": 1,
        "esi_transport_2": 1,
    }
    response = client.post("/api/v31/baseline", json={"data": payload})
    assert response.status_code == 201
    res = response.json()
    assert res["status"] == "success"
    assert "study_id" in res
    assert res["scores"]["esi_100"] == 40.0
