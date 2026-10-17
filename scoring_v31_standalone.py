"""Standalone V3.1 scoring for mock REDCap service.

Ported from NDS_Team handover, adapted to work without data-platform dependencies.
"""
from dataclasses import dataclass
from fractions import Fraction
import hashlib
import json
from pathlib import Path

ALGORITHM = 'NEPS-V3.1-provisional-corrected-1;complete-items-only;equal-dimensions'
UNAVAILABLE = frozenset({'missing', 'refused', 'unknown', 'not_applicable', 'invalid'})

# BRS reverse-scored items (6-raw in source direction)
BRS_REVERSE = {'brs_02', 'brs_04', 'brs_06'}

# Core 73 field definitions
CORE_73_FIELDS = [
    # EPI (10 items, 1-5 scale)
    'epi_expectations_1', 'epi_expectations_2',
    'epi_failure_1', 'epi_failure_2',
    'epi_caregivers_1', 'epi_caregivers_2',
    'epi_future_1', 'epi_future_2',
    'epi_progress_1', 'epi_progress_2',
    # ESI (10 items, 0-4 scale)
    'esi_finstrain_1', 'esi_finstrain_2',
    'esi_food_1', 'esi_food_2',
    'esi_educost_1', 'esi_educost_2',
    'esi_materials_1', 'esi_materials_2',
    'esi_transport_1', 'esi_transport_2',
    # SBI (19 items, 1-5 scale)
    'sbi_loved_1', 'sbi_loved_2', 'sbi_loved_3', 'sbi_loved_4',
    'sbi_loved_5', 'sbi_loved_6', 'sbi_loved_7', 'sbi_loved_8',
    'sbi_comm_1', 'sbi_comm_2', 'sbi_comm_3', 'sbi_comm_4',
    'sbi_self_1', 'sbi_self_2', 'sbi_self_3', 'sbi_self_4',
    'sbi_help_1', 'sbi_help_2', 'sbi_help_3',
    # K6 (6 items, 0-4 scale)
    'k6_1', 'k6_2', 'k6_3', 'k6_4', 'k6_5', 'k6_6',
    # BRS (6 items, 1-5 scale, 02/04/06 reverse)
    'brs_01', 'brs_02', 'brs_03', 'brs_04', 'brs_05', 'brs_06',
    # MSPSS (12 items, 1-7 scale)
    'mspss_01', 'mspss_02', 'mspss_03', 'mspss_04', 'mspss_05', 'mspss_06',
    'mspss_07', 'mspss_08', 'mspss_09', 'mspss_10', 'mspss_11', 'mspss_12',
    # GSE (10 items, 1-4 scale)
    'gse_01', 'gse_02', 'gse_03', 'gse_04', 'gse_05', 'gse_06',
    'gse_07', 'gse_08', 'gse_09', 'gse_10',
]

# Valid code ranges per instrument
VALID_RANGES = {
    # EPI: 1-5
    **{f: (1, 5) for f in CORE_73_FIELDS if f.startswith('epi_')},
    # ESI: 0-4
    **{f: (0, 4) for f in CORE_73_FIELDS if f.startswith('esi_')},
    # SBI: 1-5
    **{f: (1, 5) for f in CORE_73_FIELDS if f.startswith('sbi_')},
    # K6: 0-4
    **{f: (0, 4) for f in CORE_73_FIELDS if f.startswith('k6_')},
    # BRS: 1-5
    **{f: (1, 5) for f in CORE_73_FIELDS if f.startswith('brs_')},
    # MSPSS: 1-7
    **{f: (1, 7) for f in CORE_73_FIELDS if f.startswith('mspss_')},
    # GSE: 1-4
    **{f: (1, 4) for f in CORE_73_FIELDS if f.startswith('gse_')},
}


@dataclass(frozen=True)
class ItemIssue:
    field: str
    state: str


@dataclass(frozen=True)
class Score:
    value: Fraction | None
    issues: tuple[ItemIssue, ...] = ()


@dataclass(frozen=True)
class ScoringResult:
    scores: dict[str, Score]
    algorithm_version: str
    provisional: bool = True


def composite(epi, esi, sbi, mhdi, pfi):
    """NSES composite calculation from the handover.
    
    Formula: (30*EPI + 25*ESI + 20*SBI + 20*MHDI + 5*(100-PFI)) / 100
    """
    values = [Fraction(str(v)) for v in (epi, esi, sbi, mhdi, pfi)]
    if any(v < 0 or v > 100 for v in values):
        raise ValueError('Component score outside 0–100')
    a, b, c, d, e = values
    return (30*a + 25*b + 20*c + 20*d + 5*(100-e))/100


class V31Scorer:
    """Standalone V3.1 scorer for mock service."""
    
    def __init__(self):
        self.reverse = BRS_REVERSE
        code_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        self.version = ALGORITHM + ':' + code_hash[:16]
    
    def score(self, responses, *, missingness=None, epi_applicable=False):
        """Score V3.1 responses.
        
        Args:
            responses: Dict of field_name -> value
            missingness: Dict of field_name -> semantic state (optional)
            epi_applicable: Boolean (default False, prevents guessing for out-of-school)
        
        Returns:
            ScoringResult with all subscale scores and NSES composite
        """
        missingness = missingness or {}
        
        # Validate missingness
        if set(missingness) - set(CORE_73_FIELDS):
            raise ValueError('Unsupported semantic missingness field')
        if any(v not in UNAVAILABLE for v in missingness.values()):
            raise ValueError('Invalid semantic missingness state')
        
        parsed, issues = {}, {}
        
        # Parse and validate responses
        for field in CORE_73_FIELDS:
            raw = responses.get(field)
            state = missingness.get(field)
            
            if state is None:
                if raw is None or raw == '':
                    state = 'missing'
                elif type(raw) not in (str, int):
                    state = 'invalid'
                else:
                    lower, upper = VALID_RANGES[field]
                    try:
                        val = int(raw)
                        if val < lower or val > upper:
                            state = 'invalid'
                    except (ValueError, TypeError):
                        state = 'invalid'
            
            if state:
                issues[field] = ItemIssue(field, state)
            else:
                parsed[field] = Fraction(int(raw))
        
        # Calculate subscale scores
        def subscale_score(fields, lower, upper):
            """Calculate mean score for a subscale (0-100)."""
            if not fields:
                return Score(None, ())
            
            valid = [f for f in fields if f not in issues]
            if not valid:
                return Score(None, tuple(issues[f] for f in fields))
            
            # Apply reverse scoring for BRS items
            values = []
            for f in valid:
                val = parsed[f]
                if f in self.reverse:
                    val = 6 - val  # Reverse 1-5 to 5-1
                values.append(val)
            
            mean_val = sum(values) / len(values)
            # Scale to 0-100
            scaled = (mean_val - lower) / (upper - lower) * 100
            return Score(Fraction(scaled))
        
        # EPI (10 items, 1-5 scale)
        epi_fields = [f for f in CORE_73_FIELDS if f.startswith('epi_')]
        epi_score = subscale_score(epi_fields, 1, 5)
        
        # ESI (10 items, 0-4 scale)
        esi_fields = [f for f in CORE_73_FIELDS if f.startswith('esi_')]
        esi_score = subscale_score(esi_fields, 0, 4)
        
        # SBI (19 items, 1-5 scale)
        sbi_fields = [f for f in CORE_73_FIELDS if f.startswith('sbi_')]
        sbi_score = subscale_score(sbi_fields, 1, 5)
        
        # K6 (6 items, 0-4 scale) - MHDI index
        k6_fields = [f for f in CORE_73_FIELDS if f.startswith('k6_')]
        k6_score = subscale_score(k6_fields, 0, 4)
        k6_total = k6_score.value * 24 / 100 if k6_score.value is not None else None
        
        # BRS (6 items, 1-5 scale)
        brs_fields = [f for f in CORE_73_FIELDS if f.startswith('brs_')]
        brs_score = subscale_score(brs_fields, 1, 5)
        
        # MSPSS (12 items, 1-7 scale)
        mspss_fields = [f for f in CORE_73_FIELDS if f.startswith('mspss_')]
        mspss_score = subscale_score(mspss_fields, 1, 7)
        
        # GSE (10 items, 1-4 scale)
        gse_fields = [f for f in CORE_73_FIELDS if f.startswith('gse_')]
        gse_score = subscale_score(gse_fields, 1, 4)
        
        # PFI (BRS + MSPSS + GSE) - Protective Factors Index
        pfi_components = [brs_score, mspss_score, gse_score]
        if all(s.value is not None for s in pfi_components):
            pfi_value = sum(s.value for s in pfi_components) / 3
            pfi_score = Score(Fraction(pfi_value))
        else:
            pfi_score = Score(None, tuple(i for s in pfi_components for i in s.issues))
        
        # Handle EPI applicability
        if not epi_applicable:
            epi_score = Score(None, epi_score.issues + (ItemIssue('EPI', 'applicability_unverified'),))
        
        # Calculate NSES composite
        components = [epi_score, esi_score, sbi_score, k6_score, pfi_score]
        if all(s.value is not None for s in components):
            nses_value = composite(
                epi_score.value, esi_score.value, sbi_score.value,
                k6_score.value, pfi_score.value
            )
            nses_score = Score(Fraction(nses_value))
        else:
            nses_score = Score(None, tuple(i for s in components for i in s.issues))
        
        return ScoringResult({
            'EPI': epi_score,
            'ESI': esi_score,
            'SBI': sbi_score,
            'MHDI': k6_score,
            'K6_total': Score(Fraction(k6_total) if k6_total is not None else None),
            'BRS_100': brs_score,
            'MSPSS_100': mspss_score,
            'GSE_100': gse_score,
            'PFI': pfi_score,
            'NSES': nses_score,
        }, self.version, provisional=True)
