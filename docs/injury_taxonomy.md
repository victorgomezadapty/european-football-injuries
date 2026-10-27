# Draft injury taxonomy

Primary analyses retain source labels, including case. The complete observed label inventory with frequencies is `reports/tables/distribution_injury_type_raw.csv`. Case/whitespace variants are separately listed in `label_normalization_variants.csv`. Labels are never silently combined in burden rankings.

`injury_taxonomy_draft.csv` proposes a broad group only where a label explicitly mentions a tissue or identifiable illness/non-injury category. Every row is marked `draft_requires_review`. More than one matching rule yields `Unresolved`, preventing implicit priority from resolving ambiguous phrases. Missing and vague labels also remain unresolved.

| Draft group | Rule rationale | Important exclusions |
| --- | --- | --- |
| Muscle | Explicit muscle/muscular wording | Hamstring/calf/groin pain alone does not establish tissue pathology |
| Ligament | Explicit ligament or ACL wording | Generic sprains remain unresolved |
| Tendon | Explicit tendon, tendinitis or Achilles wording | Region alone is not a verified tissue diagnosis |
| Joint | Explicit meniscus, cartilage, dislocation, capsular wording | Vague knee/ankle problems unresolved |
| Bone | Explicit fracture/broken or bone edema wording | Ambiguous multiple tissue matches unresolved |
| Illness | Explicit matched infectious/illness labels | Unmatched diagnoses remain unresolved rather than guessed |
| Non-injury absence | Exact quarantine, rest, fitness, suspension, international duty labels | Fitness may follow injury; classification is descriptive only |
| Unresolved | Missing, vague, unmatched or multiply matched labels | Requires review; never treated as a single anatomical region |

Rules are in `src/features/injury_features.py` and the export records which rules matched. The inventory reveals possible clinical synonyms such as syndesmosis/syndesmotic ligament labels and muscle-fiber variants. These require source/clinical review before a mapping is accepted. No anatomical-region recurrence or `prior_same_group_count` is calculated from this draft.

Next review should establish approved exact-label mappings, anatomical region, tissue, clinical specificity, illness/non-injury status, laterality availability and rationale per mapping. Keep a versioned review log. Do not infer confirmed clinical reinjury from a repeated category.
