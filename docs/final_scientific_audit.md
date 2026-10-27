# Final scientific and computational audit

Audit date: 27 October 2026. Reviewed the checksum-registered Kaggle version 2 CSV, generated descriptive outputs, history/recurrence implementation and existing boundary tests.

## Decision

The project supports a reproducible analysis of recorded football absence events and their reported consequences. Frequency, continuous duration, reported match loss, cumulative episode burden, duplicate sensitivity and descriptive histories are defensible with the documented definitions. No consequential computational defect was found in the reviewed history, recurrence or interval-union functions. No source-code change was required by this audit.

The public site uses aggregate results, without individual names or histories. Its source-record and candidate-collapsed filters must preserve the stated observation unit and use exact precomputed subset summaries. Completion does not require a prediction or survival model that the source cannot justify.

## Verification

- Existing independent source reconciliation: 15,603 rows, 11 columns, 563,314 reported episode-days and 85,928 reported match losses. See `reports/verification.json`.
- All 11 existing event-integrity tests passed during this audit.
- Independently recomputed all 15,603 prior-record counts using cumulative sums over player/start-date batches. They matched the exported values.
- Independently recomputed all same-label prior counts over player/label/start-date batches. They matched the exported values.
- Independently checked same-label-after-recorded-end counts with a self-join requiring an earlier onset, valid prior interval and prior end strictly before current onset. They matched the exported values.
- The source has no observed missing starts/ends, negative durations, end-before-start records or exact whole-row duplicates. Every reported duration equals exclusive date difference plus one, consistent with inclusive recorded dates.

These checks validate arithmetic and internal consistency. They do not establish original ascertainment, clinical accuracy, identity, or completeness of injury recording.

## Repeated episodes and attribution

The 1,973 flagged rows form **981 candidate groups**, containing **992 extra rows** beyond one row per group. A candidate key combines recorded-name surrogate, normalized label and start/end dates.

All 981 groups span multiple club labels. None spans multiple source seasons. None conflicts in reported days or games missed within the candidate group. These observations support a repeated-history/context hypothesis, but do not independently adjudicate clinical events or authoritative club attribution.

| View | Records | Reported episode-days | Reported match losses |
| --- | --- | --- | --- |
| Primary source records | 15,603 | 563,314 | 85,928 |
| Candidate-collapsed sensitivity | 14,611 | 532,422 | 81,226 |

Candidate collapsing reduces records by 6.4%, episode-days by 5.5% and match losses by 5.5%. It is a sensitivity scenario, not a verified clinical episode count. The representative first source row cannot decide which club incurred the loss. Registration/transfer dates and original-record review would be needed for that attribution.

## Identity, histories and gaps

The 4,081 distinct names are recorded-name values, not verified player identities. Hashing a name provides reproducibility, not identity evidence; homonyms can combine people and spelling variants can split one person.

Same-day records correctly do not enter one another's prior history. A tied latest earlier onset makes the previous-end gap unavailable. Missing starts cannot enter chronological counts. Full-history totals remain retrospective and must not be assigned to earlier injuries as onset predictors.

The primary view contains 361 records overlapping an earlier valid inclusive interval; the candidate view contains 339. The latest-record gap is available for 10,084 primary records and 10,505 candidate records, including 92 and 99 negative gaps respectively. Candidate collapsing resolves some ties, making additional gaps calculable; the differing negative-gap counts are therefore not contradictory.

An overlap with any earlier interval and a gap from the latest earlier onset are different measures. A positive gap does not establish healthy, eligible or selected time. Repeated labels, including labels repeated after a recorded end, are not confirmed clinical reinjuries: laterality, diagnosis, resolution and new-event status remain unverified.

## Taxonomy and comparisons

The draft rules leave **8,505 records across 153 labels unresolved**, or 54.5% of records. This conservative choice avoids inventing tissue pathology from vague regional symptoms or ambiguous wording. Raw labels are appropriate for the main burden rankings. Draft groups must not silently exclude unresolved records or imply clinically validated classification. Fitness can be a post-injury state; its draft non-injury designation does not prove an absence unrelated to injury.

No full healthy squad roster, player-hours, registration/eligibility window or complete fixture denominator is present. More records by league, club, age or position cannot establish greater individual injury risk. The first/last injury dates cannot serve as an observation denominator.

Monthly summaries assign an episode's full burden to its onset month. They represent burden associated with records starting in that month, not actual absence-days or match losses incurred within that calendar month. Source-season summaries likewise use source context rather than day-by-day allocation of cross-season intervals.

All records have at least one reported day and missed game. This describes the file and does not establish that zero-game absences never occurred. Zero missingness does not rule out selection or reporting bias before collection. Recorded age timing is unverified; age comparisons remain event-weighted, unadjusted descriptions. Sample sizes should accompany rare-label medians.

## Survival and predictive modeling

A clinical time-to-return analysis needs verified start/end meaning, actual versus expected return, observation cutoffs, ongoing/excluded absences, an event/censoring indicator and repeated-player handling. These inputs are not independently established. Ends extending beyond a season do not themselves identify censoring or actual return.

A Kaplan-Meier curve treating every recorded end as an observed clinical return would add unverified assumptions while mostly re-expressing the duration distribution. No prospective survival model is justified by this review. An empirical duration curve, if shown, must describe the fraction of recorded intervals exceeding a duration, not a player's recovery probability.

The dataset also cannot establish true availability percentages, exposure-based incidence, future individual injury probability or workload causation. Completing the evidence, discussion, reproducibility and public experience is scientifically stronger than adding unsupported estimates.

## Public presentation conditions

- Lead with recorded absence burden and state the observation unit.
- Present source-record and candidate-collapsed results with their retention rules.
- Distinguish summed episode-days, union of recorded dates and true availability.
- Keep raw labels, sample sizes, provenance and draft-taxonomy status visible.
- Separate the project's observations from the external research discussed in the bibliography.
- Publish reproducible code, source/checksum instructions, aggregate outputs, limitations and tests.
- Keep survival, external exposure integration and prediction as evidence-dependent extensions.

This audit changed no raw data, generated analytical tables, website or publication settings.
