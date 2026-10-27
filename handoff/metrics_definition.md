# Metrics registry

| Metric | Definition | Unit / denominator | Main limitation |
| --- | --- | --- | --- |
| injury_count | Number of retained source records | Records, no exposure denominator | Includes absences and candidate duplicates |
| median_days_out | Median valid reported duration | Days per nonmissing record | Repeated events and injury mix; no prognosis |
| total_days_out | Sum valid reported days | Episode-days | Overlap and repeated records double count |
| total_games_missed | Sum valid reported missed matches | Match losses summed over records | No unique fixture reconciliation |
| prior count | Count with strictly earlier recorded starts | Earlier records within dataset | Not complete lifetime history or source knowledge at onset |
| previous_same_injury_count | Earlier starts with same normalized label | Recorded labels within name | No side/anatomical identity or clinical reinjury |
| days_since_previous_injury | Current start minus latest earlier record end | Date difference in days | Retrospective; ties/missing end unavailable; negative overlap |
| same_label_after_recorded_end_count | Earlier same-label valid intervals ending before current start | Recorded intervals | End is not verified recovery; no reinjury inference |
| recorded_interval_union_days | Unique dates in valid closed intervals within recorded name | Recorded calendar dates | No observation/eligibility denominator or proof of complete absence |
| career_injury_count_in_dataset | Full-history retained record count per name | Records | Name identity provisional; future leakage at earlier dates |

Each numeric summary exports valid-outcome sample counts. No availability percentage, player-hours incidence, workload metric or prospective injury probability is calculated. Source and candidate-collapsed sensitivity views use the same metric definitions but different record-retention assumptions.
