"""V3.1 Baseline data generator for mock REDCap service.

Generates the full 223-field baseline screening per NEPS Master CRF V3.1.
This is a single-timepoint baseline instrument, not longitudinal.
"""
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json

from scoring_v31_standalone import V31Scorer, CORE_73_FIELDS, VALID_RANGES

# Field groupings by form (from data_contract_v31.json)
FORM_FIELD_GROUPS = {
    'neps31_registry': [
        'study_id', 'country', 'site_id', 'site_setting', 'recruit_src',
        'screen_date', 'crf_version', 'form_lang', 'age_years', 'sex_report',
        'study_resident', 'screen_form_complete',
    ],
    'neps31_screening': CORE_73_FIELDS,  # 73 core clinical items
    'neps31_cohort_interest': [
        'willing_24m', 'contact_24m', 'wp3_willing', 'wp4_willing', 'wp6_willing',
    ],
    'neps31_extended_baseline': [
        'currently_school', 'ever_school', 'school_level', 'not_school_reason',
        'self_school_perf', 'household_language', 'internet_home', 'father_ed',
        'mother_ed', 'household_members', 'living_arrangement', 'caregiver_prim',
        'parent_alive', 'caregiver_abroad', 'caregiver_education', 'family_mh_hist',
        'school_days_missed', 'work_status', 'care_duties', 'epix_exams_1', 'epix_exams_2',
        'epix_teacher_1', 'epix_teacher_2', 'asset_01', 'asset_02', 'asset_03', 'asset_04',
        'asset_05', 'asset_06', 'asset_07', 'asset_08', 'asset_water', 'asset_toilet',
        'asset_floor', 'asset_sleeprooms', 'sbi_exp_gate', 'sbi_exper_1', 'sbi_exper_2',
        'sbi_exper_3', 'sbi_exper_4', 'seek_01', 'seek_02', 'seek_03', 'seek_04',
        'seek_08', 'ypw_01', 'ypw_02', 'ypw_03', 'ypw_04', 'ypw_05', 'ypw_06',
        'ypw_07', 'ypw_08', 'ypw_09', 'ypw_10', 'ypw_11', 'ypw_12', 'ypw_13',
        'ypw_14', 'bully_30d', 'attack_12m', 'fight_12m', 'substance_ever',
        'bully_type', 'attack_freq', 'attack_by', 'substance_30d', 'caregiver_substance',
        'family_disrupt_current', 'community_safety', 'social_family_contact',
        'social_peer_contact', 'social_community', 'sleep_hunger_context',
    ],
    'neps31_yeb': [
        'yeb_01', 'yeb_02', 'yeb_03', 'yeb_04', 'yeb_05', 'yeb_06',
        'yeb_07', 'yeb_08', 'yeb_09', 'yeb_10', 'yeb_11', 'yeb_12',
        'yeb_13', 'yeb_14', 'yeb_imp_study', 'yeb_imp_work', 'yeb_imp_home',
        'yeb_imp_rel', 'yeb_imp_activities',
    ],
    'neps31_ycad': [
        'ycad_01', 'ycad_02', 'ycad_03', 'ycad_04', 'ycad_05', 'ycad_06',
        'ycad_07', 'ycad_08', 'ycad_09', 'ycad_10', 'ycad_11', 'ycad_12',
        'ycad_13', 'ycad_14', 'ycad_time_harm', 'ycad_time_viol', 'ycad_time_sep',
    ],
}

# Branching logic conditions
BRANCHING_CONDITIONS = {
    'epix_exams_1': {'field': 'currently_school', 'values': ['1']},
    'epix_exams_2': {'field': 'currently_school', 'values': ['1']},
    'epix_teacher_1': {'field': 'currently_school', 'values': ['1']},
    'epix_teacher_2': {'field': 'currently_school', 'fields': ['1']},
    'sbi_exper_1': {'field': 'sbi_exp_gate', 'values': ['1']},
    'sbi_exper_2': {'field': 'sbi_exp_gate', 'values': ['1']},
    'sbi_exper_3': {'field': 'sbi_exp_gate', 'values': ['1']},
    'sbi_exper_4': {'field': 'sbi_exp_gate', 'values': ['1']},
    'yeb_imp_study': {'field': 'ever_school', 'values': ['1']},
    'yeb_imp_work': {'field': 'work_status', 'values': ['1', '2', '3']},
    'attack_freq': {'field': 'attack_12m', 'values': ['2']},
    'attack_freq_missing': {'field': 'attack_12m', 'values': ['2']},
    'attack_by': {'field': 'attack_12m', 'values': ['1', '2']},
    'ycad_time_harm': {'gate': 'any_maltreatment'},
    'ycad_time_viol': {'gate': 'any_violence'},
    'ycad_time_sep': {'gate': 'any_separation'},
}

# Derived fields (keep null per contract)
DERIVED_FIELDS_NULL = {
    'age_band', 'brs_raw', 'mspss_raw', 'gse_raw', 'k6_raw',
    'epi_100', 'esi_100', 'sbi_100', 'mhdi_100', 'pfi_100',
    'nses_100', 'screen_score_status', 'stressor_burden_count',
    'stressor_burden_class', 'stressor_profile', 'iwi_score',
}

# Country-site mapping
COUNTRY_SITES = {
    'Ghana': ['Kumasi', 'Accra', 'Ho', 'Tamale'],
    'Sierra Leone': ['Freetown', 'Bo', 'Makeni'],
    'Tanzania': ['Dar es Salaam', 'Mwanza', 'Arusha'],
}

SCHOOLS = {
    'Kumasi': ['KNUST SHS', 'Prempeh College', 'Opoku Ware SHS'],
    'Accra': ['Accra Academy', 'Achimota School', 'Presbyterian Boys'],
    'Ho': ['Mawuli School', 'OLA SHS', 'Sogakope SHS'],
    'Tamale': ['Tamale SHS', 'Ghana SHS', 'St. Charles'],
    'Freetown': ['Prince of Wales', 'Methodist Boys', 'Annie Walsh'],
    'Bo': ['Bo Government', 'Christ the King', 'St. Francis'],
    'Makeni': ['Makeni Comprehensive', 'Bombali', 'St. Joseph'],
    'Dar es Salaam': ['Ilboru', 'Tambaza', 'Kisutu'],
    'Mwanza': ['Mwanza Academy', 'St. Augustine', 'VETA'],
    'Arusha': ['Arusha Secondary', 'Korogwe', 'Moshi'],
}


class V31BaselineGenerator:
    """Generates V3.1 baseline screening data."""
    
    def __init__(self, seed: int = 42):
        random.seed(seed)
        self.scorer = V31Scorer()
    
    def generate_participant_id(self, index: int) -> str:
        """Generate MOCK ID without country encoding (NEW format)."""
        return f"MOCK-{index:04d}"
    
    def generate_baseline_record(self, participant_id: str) -> Dict[str, Any]:
        """Generate a complete V3.1 baseline record for one participant."""
        record = {}
        
        # neps31_registry (administrative fields)
        record['study_id'] = participant_id
        record['country'] = random.choice(['Ghana', 'Sierra Leone', 'Tanzania'])
        record['site_id'] = random.choice(COUNTRY_SITES[record['country']])
        record['site_setting'] = random.choice(['Urban', 'Peri-urban', 'Rural'])
        record['recruit_src'] = random.choice(['School', 'Technical or vocational', 'Tertiary institution', 'Community'])
        record['screen_date'] = (datetime.now() - timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d")
        record['crf_version'] = '3.1'
        record['form_lang'] = random.choice(['English', 'Akan/Twi', 'Krio', 'Kiswahili', 'Other approved language'])
        record['age_years'] = random.randint(12, 24)
        record['sex_report'] = random.choice(['1', '2', '99'])  # Boy/male, Girl/female, Prefer not
        record['study_resident'] = random.choice(['0', '1', '98', '99'])
        record['screen_form_complete'] = '2'  # Complete and reviewed
        
        # neps31_cohort_interest (5 fields)
        record['willing_24m'] = random.choice(['0', '1'])
        record['contact_24m'] = random.choice(['0', '1'])
        record['wp3_willing'] = random.choice(['0', '1'])
        record['wp4_willing'] = random.choice(['0', '1'])
        record['wp6_willing'] = random.choice(['0', '1'])
        
        # neps31_extended_baseline (74 fields)
        record['currently_school'] = random.choice(['0', '1'])
        record['ever_school'] = random.choice(['0', '1'])
        record['school_level'] = random.choice(['Primary', 'Junior Secondary', 'Senior Secondary', 'University', 'Vocational', 'Not in school'])
        record['not_school_reason'] = '' if record['currently_school'] == '1' else random.choice(['', 'Graduated', 'Working', 'Family responsibilities', 'Health'])
        record['self_school_perf'] = random.choice(['Excellent', 'Good', 'Average', 'Below average', 'Poor'])
        record['household_language'] = random.choice(['English', 'Akan/Twi', 'Krio', 'Kiswahili', 'Other'])
        record['internet_home'] = random.choice(['0', '1'])
        record['father_ed'] = random.choice(['0', '1', '2', '3', '4', '96', '98', '99'])
        record['mother_ed'] = random.choice(['0', '1', '2', '3', '4', '96', '98', '99'])
        record['household_members'] = random.randint(1, 15)
        record['living_arrangement'] = random.choice(['1', '2', '3', '4', '5', '6', '7'])
        record['caregiver_prim'] = random.choice(['1', '2', '3', '4', '5', '6', '7', '99'])
        record['parent_alive'] = random.choice(['1', '2', '3', '4', '98', '99'])
        record['caregiver_abroad'] = random.choice(['0', '1', '98', '99'])
        record['caregiver_education'] = random.choice(['0', '1', '2', '3', '4', '96', '98', '99'])
        record['family_mh_hist'] = random.choice(['0', '1', '98', '99'])
        record['school_days_missed'] = random.randint(0, 30)
        record['work_status'] = random.choice(['0', '1', '2', '3', '99'])
        record['care_duties'] = random.choice(['0', '1', '2', '3', '4', '96'])
        
        # Assets (8 fields)
        for i in range(1, 9):
            record[f'asset_0{i}'] = random.choice(['0', '1', '98', '99'])
        record['asset_water'] = random.choice(['1', '2', '3', '4', '5', '6', '7', '8', '9', '98'])
        record['asset_toilet'] = random.choice(['1', '2', '3', '4', '5', '6', '98'])
        record['asset_floor'] = random.choice(['1', '2', '3', '4', '5', '98'])
        record['asset_sleeprooms'] = random.randint(0, 10)
        
        # School pressure (conditional)
        if record['currently_school'] == '1':
            record['epix_exams_1'] = random.randint(1, 5)
            record['epix_exams_2'] = random.randint(1, 5)
            record['epix_teacher_1'] = random.randint(1, 5)
            record['epix_teacher_2'] = random.randint(1, 5)
        else:
            record['epix_exams_1'] = ''  # BLANK (not 96)
            record['epix_exams_2'] = ''
            record['epix_teacher_1'] = ''
            record['epix_teacher_2'] = ''
        
        # Stigma gate
        record['sbi_exp_gate'] = random.choice(['0', '1', '96', '98', '99'])
        
        # Experienced stigma (conditional)
        if record['sbi_exp_gate'] == '1':
            for i in range(1, 5):
                record[f'sbi_exper_{i}'] = random.randint(0, 4)
        else:
            for i in range(1, 5):
                record[f'sbi_exper_{i}'] = ''  # BLANK
        
        # Help-seeking beliefs (5 fields)
        record['seek_01'] = random.randint(1, 5)
        record['seek_02'] = random.randint(1, 5)
        record['seek_03'] = random.randint(1, 5)
        record['seek_04'] = random.randint(1, 5)
        record['seek_08'] = random.randint(1, 5)
        
        # Positive wellbeing (14 fields)
        for i in range(1, 15):
            record[f'ypw_{i:02d}'] = random.randint(0, 4)
        
        # Bullying/violence
        record['bully_30d'] = random.randint(0, 3)
        record['attack_12m'] = random.choice(['0', '1', '2', '99'])
        record['fight_12m'] = random.choice(['0', '1', '2', '99'])
        record['substance_ever'] = random.choice(['0', '1', '2', '3', '98', '99'])
        
        # Bullying type (conditional)
        if record['bully_30d'] in ['1', '2', '3']:
            record['bully_type'] = random.choice(['1', '2', '3', '4', '5', '99'])
        else:
            record['bully_type'] = ''
        
        # Attack details (conditional)
        if record['attack_12m'] == '2':
            record['attack_freq_missing'] = random.choice(['1', '98', '99'])
            if record['attack_freq_missing'] == '1':
                record['attack_freq'] = str(random.randint(2, 10))
            else:
                record['attack_freq'] = ''
            record['attack_by'] = random.choice(['1', '2', '3', '4', '99'])
        else:
            record['attack_freq_missing'] = ''
            record['attack_freq'] = ''
            record['attack_by'] = ''
        
        # Substance use
        record['substance_30d'] = random.choice(['0', '1', '2', '3', '98', '99'])
        record['caregiver_substance'] = random.choice(['0', '1', '98', '99'])
        record['family_disrupt_current'] = random.choice(['0', '1', '98', '99'])
        record['community_safety'] = random.randint(0, 4)
        
        # Social contact
        record['social_family_contact'] = random.randint(0, 4)
        record['social_peer_contact'] = random.randint(0, 4)
        record['social_community'] = random.choice(['0', '1', '96', '99'])
        record['sleep_hunger_context'] = random.randint(0, 4)
        
        # neps31_yeb (19 fields)
        for i in range(1, 15):
            record[f'yeb_{i:02d}'] = random.randint(0, 4)
        
        # YEB impact (conditional)
        if record['ever_school'] == '1' or record['currently_school'] == '1':
            record['yeb_imp_study'] = random.randint(0, 4)
        else:
            record['yeb_imp_study'] = ''
        
        if record['work_status'] in ['1', '2', '3']:
            record['yeb_imp_work'] = random.randint(0, 4)
        else:
            record['yeb_imp_work'] = ''
        
        record['yeb_imp_home'] = random.randint(0, 4)
        record['yeb_imp_rel'] = random.randint(0, 4)
        record['yeb_imp_activities'] = random.randint(0, 4)
        
        # neps31_ycad (17 fields)
        for i in range(1, 15):
            record[f'ycad_{i:02d}'] = random.choice(['0', '1', '2', '98', '99'])
        
        # YCAD timing (conditional on maltreatment)
        maltreatment_any = any(record[f'ycad_{i:02d}'] in ['1', '2'] for i in range(1, 9))
        if maltreatment_any:
            record['ycad_time_harm'] = random.choice(['1', '2', '3', '98', '99'])
        else:
            record['ycad_time_harm'] = ''
        
        # YCAD timing (conditional on violence)
        violence_any = any(record[f'ycad_{i:02d}'] in ['1', '2'] for i in range(9, 11))
        if violence_any:
            record['ycad_time_viol'] = random.choice(['1', '2', '3', '98', '99'])
        else:
            record['ycad_time_viol'] = ''
        
        # YCAD timing (conditional on separation)
        separation_any = any(record[f'ycad_{i:02d}'] in ['1', '2'] for i in range(12, 14))
        if separation_any:
            record['ycad_time_sep'] = random.choice(['1', '2', '3', '98', '99'])
        else:
            record['ycad_time_sep'] = ''
        
        # neps31_screening (73 core clinical items)
        # EPI (10 items, 1-5)
        for i in range(1, 3):
            record[f'epi_expectations_{i}'] = random.randint(1, 5)
        for i in range(1, 3):
            record[f'epi_failure_{i}'] = random.randint(1, 5)
        for i in range(1, 3):
            record[f'epi_caregivers_{i}'] = random.randint(1, 5)
        for i in range(1, 3):
            record[f'epi_future_{i}'] = random.randint(1, 5)
        for i in range(1, 3):
            record[f'epi_progress_{i}'] = random.randint(1, 5)
        
        # ESI (10 items, 0-4)
        for i in range(1, 3):
            record[f'esi_finstrain_{i}'] = random.randint(0, 4)
        for i in range(1, 3):
            record[f'esi_food_{i}'] = random.randint(0, 4)
        for i in range(1, 3):
            record[f'esi_educost_{i}'] = random.randint(0, 4)
        for i in range(1, 3):
            record[f'esi_materials_{i}'] = random.randint(0, 4)
        for i in range(1, 3):
            record[f'esi_transport_{i}'] = random.randint(0, 4)
        
        # SBI (19 items, 1-5)
        for i in range(1, 9):
            record[f'sbi_loved_{i}'] = random.randint(1, 5)
        for i in range(1, 5):
            record[f'sbi_comm_{i}'] = random.randint(1, 5)
        for i in range(1, 5):
            record[f'sbi_self_{i}'] = random.randint(1, 5)
        for i in range(1, 4):
            record[f'sbi_help_{i}'] = random.randint(1, 5)
        
        # K6 (6 items, 0-4)
        for i in range(1, 7):
            record[f'k6_{i}'] = random.randint(0, 4)
        
        # BRS (6 items, 1-5)
        for i in range(1, 7):
            record[f'brs_{i:02d}'] = random.randint(1, 5)
        
        # MSPSS (12 items, 1-7)
        for i in range(1, 13):
            record[f'mspss_{i:02d}'] = random.randint(1, 7)
        
        # GSE (10 items, 1-4)
        for i in range(1, 11):
            record[f'gse_{i:02d}'] = random.randint(1, 4)
        
        # Derived fields (null per contract)
        for field in DERIVED_FIELDS_NULL:
            record[field] = None
        
        # Add metadata
        record['_instrument'] = 'neps31_screening'
        record['_form_name'] = 'neps31_screening'
        record['_source'] = 'v31_baseline'
        record['_version'] = '3.1'
        
        return record
    
    def generate_baseline_dataset(self, count: int = 150) -> List[Dict[str, Any]]:
        """Generate V3.1 baseline records for N participants."""
        records = []
        for i in range(1, count + 1):
            participant_id = self.generate_participant_id(i)
            record = self.generate_baseline_record(participant_id)
            records.append(record)
        return records
    
    def add_missingness_patterns(self, records: List[Dict[str, Any]], missingness_rate: float = 0.05):
        """Add realistic missingness patterns (3-8% default)."""
        for record in records:
            # Random missingness for some fields
            for field in CORE_73_FIELDS:
                if random.random() < missingness_rate:
                    record[field] = ''  # BLANK (not 96)
        
        return records
    
    def score_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score V3.1 records using the standalone scorer."""
        scored_records = []
        
        for record in records:
            # Extract only the 73 core items for scoring
            core_responses = {f: record[f] for f in CORE_73_FIELDS if f in record}
            
            # Score
            result = self.scorer.score(core_responses)
            
            # Add derived scores to record (both official CRF dictionary names and convenience aliases)
            nses_val = float(result.scores['NSES'].value) if result.scores['NSES'].value is not None else None
            epi_val = float(result.scores['EPI'].value) if result.scores['EPI'].value is not None else None
            esi_val = float(result.scores['ESI'].value) if result.scores['ESI'].value is not None else None
            sbi_val = float(result.scores['SBI'].value) if result.scores['SBI'].value is not None else None
            mhdi_val = float(result.scores['MHDI'].value) if result.scores.get('MHDI') and result.scores['MHDI'].value is not None else None
            pfi_val = float(result.scores['PFI'].value) if result.scores['PFI'].value is not None else None
            k6_val = float(result.scores['K6_total'].value) if result.scores['K6_total'].value is not None else None
            brs_val = float(result.scores['BRS_100'].value) if result.scores['BRS_100'].value is not None else None
            mspss_val = float(result.scores['MSPSS_100'].value) if result.scores['MSPSS_100'].value is not None else None
            gse_val = float(result.scores['GSE_100'].value) if result.scores['GSE_100'].value is not None else None
            
            # Official dictionary fields (neps31_derived)
            record['nses_100'] = nses_val
            record['epi_100'] = epi_val
            record['esi_100'] = esi_val
            record['sbi_100'] = sbi_val
            record['mhdi_100'] = mhdi_val
            record['pfi_100'] = pfi_val
            record['k6_raw'] = k6_val
            record['brs_raw'] = brs_val
            record['mspss_raw'] = mspss_val
            record['gse_raw'] = gse_val
            record['screen_score_status'] = 'complete' if nses_val is not None else 'incomplete'
            
            # Convenience aliases
            record['nses_composite_score'] = nses_val
            record['epi_score'] = epi_val
            record['esi_score'] = esi_val
            record['sbi_score'] = sbi_val
            record['k6_total'] = k6_val
            record['brs_score'] = brs_val
            record['mspss_score'] = mspss_val
            record['gse_score'] = gse_val
            record['pfi_score'] = pfi_val
            
            record['_scoring_version'] = result.algorithm_version
            record['_scored_at'] = datetime.now().isoformat()
            
            scored_records.append(record)
        
        return scored_records


if __name__ == '__main__':
    # Generate test sample
    generator = V31BaselineGenerator(seed=42)
    records = generator.generate_baseline_dataset(5)
    records = generator.add_missingness_patterns(records, missingness_rate=0.05)
    records = generator.score_records(records)
    
    print(f"Generated {len(records)} V3.1 baseline records")
    print(f"Sample record keys: {list(records[0].keys())[:10]}")
    print(f"Sample NSES score: {records[0]['nses_composite_score']}")
