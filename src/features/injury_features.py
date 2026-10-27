"""Conservative draft taxonomy. Primary analyses retain original injury labels."""
import re
import pandas as pd

# No anatomical tissue is inferred from vague pain/problem/strain labels.
RULES = [
    ('Non-injury absence', r'^(quarantine|rest|fitness|suspension|international duty)$'),
    ('Illness', r'corona|covid|influenza|\bflu\b|\bcold\b|^ill$|illness|virus|infection|tonsillitis|appendicitis'),
    ('Ligament', r'ligament|\bacl\b'),
    ('Tendon', r'tendon|tendinitis|tendonitis|achilles'),
    ('Bone', r'fracture|broken|bone edema|bone oedema'),
    ('Muscle', r'\bmuscle\b|\bmuscular\b'),
    ('Joint', r'meniscus|cartilage|dislocation|capsular'),
]


def draft_taxonomy(labels):
    rows=[]
    for label, count in labels.value_counts(dropna=False).items():
        key = '' if pd.isna(label) else str(label).casefold().strip()
        matches = [group for group, pattern in RULES if re.search(pattern,key)]
        rows.append({'injury_type_raw':label, 'record_count':count,
                     'injury_group_draft': matches[0] if len(matches)==1 else 'Unresolved',
                     'taxonomy_status':'draft_requires_review',
                     'rule_matches':'; '.join(matches),
                     'normalization_key':re.sub(r'\s+',' ',key) if key else pd.NA})
    return pd.DataFrame(rows)
