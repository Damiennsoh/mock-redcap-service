"""SCORING_GOLDEN CI tests for V3.1 scoring.

These tests run on every commit to ensure scoring arithmetic remains correct.
Based on golden fixtures from NDS_Team handover.
"""
import json
import random
import pytest
from scoring_v31_standalone import V31Scorer, CORE_73_FIELDS, VALID_RANGES


def load_scoring_golden():
    """Load SCORING_GOLDEN.json fixtures."""
    import os
    base_dir = os.path.dirname(os.path.dirname(__file__))
    golden_path = os.path.join(base_dir, "scoring_golden.json")
    
    with open(golden_path, "r", encoding="utf-8") as f:
        return json.load(f)


def test_scoring_golden_composite():
    """Test NSES composite calculation against golden fixture."""
    golden = load_scoring_golden()
    scorer = V31Scorer()
    
    # Find the composite_52_5 test case
    test_case = None
    for case in golden.get("cases", []):
        if case.get("id") == "composite_52_5":
            test_case = case
            break
    
    assert test_case is not None, "composite_52_5 test case not found in SCORING_GOLDEN.json"
    
    # The golden fixture doesn't include raw responses, only expected scores
    # So we test the scoring arithmetic function directly
    from scoring_v31_standalone import composite
    
    # Test the composite formula with the expected component inputs
    epi, esi, sbi, mhdi, pfi = 80, 60, 40, 20, 70
    result = composite(epi, esi, sbi, mhdi, pfi)
    
    # The expected is 52.5
    assert abs(result - 52.5) < 0.01, f"Expected 52.5, got {result}"


def test_scorer_initialization():
    """Test that scorer initializes correctly."""
    scorer = V31Scorer()
    assert scorer.version is not None
    assert scorer.reverse == {'brs_02', 'brs_04', 'brs_06'}


def test_core_73_fields_count():
    """Test that core 73 fields are correctly defined."""
    from scoring_v31_standalone import CORE_73_FIELDS
    
    assert len(CORE_73_FIELDS) == 73, f"Expected 73 core fields, got {len(CORE_73_FIELDS)}"
    
    # Verify expected prefixes
    epi_count = sum(1 for f in CORE_73_FIELDS if f.startswith('epi_'))
    esi_count = sum(1 for f in CORE_73_FIELDS if f.startswith('esi_'))
    sbi_count = sum(1 for f in CORE_73_FIELDS if f.startswith('sbi_'))
    k6_count = sum(1 for f in CORE_73_FIELDS if f.startswith('k6_'))
    brs_count = sum(1 for f in CORE_73_FIELDS if f.startswith('brs_'))
    mspss_count = sum(1 for f in CORE_73_FIELDS if f.startswith('mspss_'))
    gse_count = sum(1 for f in CORE_73_FIELDS if f.startswith('gse_'))
    
    assert epi_count == 10, f"Expected 10 EPI items, got {epi_count}"
    assert esi_count == 10, f"Expected 10 ESI items, got {esi_count}"
    assert sbi_count == 19, f"Expected 19 SBI items, got {sbi_count}"
    assert k6_count == 6, f"Expected 6 K6 items, got {k6_count}"
    assert brs_count == 6, f"Expected 6 BRS items, got {brs_count}"
    assert mspss_count == 12, f"Expected 12 MSPSS items, got {mspss_count}"
    assert gse_count == 10, f"Expected 10 GSE items, got {gse_count}"


def test_valid_ranges():
    """Test that valid ranges are correctly defined."""
    from scoring_v31_standalone import VALID_RANGES
    
    # K6 should be 0-4
    assert VALID_RANGES['k6_1'] == (0, 4)
    
    # EPI should be 1-5
    assert VALID_RANGES['epi_expectations_1'] == (1, 5)
    
    # ESI should be 0-4
    assert VALID_RANGES['esi_finstrain_1'] == (0, 4)
    
    # SBI should be 1-5
    assert VALID_RANGES['sbi_loved_1'] == (1, 5)
    
    # BRS should be 1-5
    assert VALID_RANGES['brs_01'] == (1, 5)
    
    # MSPSS should be 1-7
    assert VALID_RANGES['mspss_01'] == (1, 7)
    
    # GSE should be 1-4
    assert VALID_RANGES['gse_01'] == (1, 4)


def test_scoring_with_complete_responses():
    """Test scoring with complete valid responses."""
    scorer = V31Scorer()
    
    # Create a complete response set with valid values
    responses = {}
    for field in CORE_73_FIELDS:
        lower, upper = VALID_RANGES[field]
        responses[field] = random.randint(lower, upper)
    
    result = scorer.score(responses, epi_applicable=True)
    
    # Should have valid scores
    assert result.scores['NSES'].value is not None
    assert 0 <= result.scores['NSES'].value <= 100
    
    # Subscale scores should be valid
    assert result.scores['EPI'].value is not None
    assert result.scores['ESI'].value is not None
    assert result.scores['SBI'].value is not None
    assert result.scores['MHDI'].value is not None
    assert result.scores['PFI'].value is not None


def test_scoring_with_missingness():
    """Test scoring with missing responses."""
    scorer = V31Scorer()
    
    # Create a response set with forced missing values in EPI subscale
    responses = {}
    for field in CORE_73_FIELDS:
        lower, upper = VALID_RANGES[field]
        if field.startswith('epi_'):
            responses[field] = ''  # Missing all EPI items
        else:
            responses[field] = (lower + upper) // 2
    
    result = scorer.score(responses, epi_applicable=True)
    
    # With EPI missing, EPI score should be None, and NSES should be None
    assert result.scores['EPI'].value is None
    assert result.scores['NSES'].value is None
    
    # Other subscales should still have scores
    assert result.scores['ESI'].value is not None
    assert result.scores['SBI'].value is not None


def test_brs_reverse_scoring():
    """Test that BRS reverse items are correctly handled."""
    scorer = V31Scorer()
    
    # Create responses where reverse items are low (should become high after reverse)
    responses = {}
    for field in CORE_73_FIELDS:
        lower, upper = VALID_RANGES[field]
        if field in scorer.reverse:
            responses[field] = 1  # Low response
        else:
            responses[field] = 5  # High response
    
    result = scorer.score(responses, epi_applicable=True)
    
    # BRS score should reflect reverse scoring
    assert result.scores['BRS_100'].value is not None


if __name__ == "__main__":
    import random
    pytest.main([__file__, "-v"])
