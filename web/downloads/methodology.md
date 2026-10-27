# Milestone 1 methodology

## Observation unit and population

The source is an absence-event table. It contains injuries, illnesses and other absence reasons for recorded players. It has no complete roster of healthy players and no exposure observations. Use `record_count`/`injury_count` with the stated observation unit, not incidence or individual injury risk. Medical diagnoses, laterality and return clearance are not independently verified.

## Parsing and missing data

Load all CSV fields as UTF-8 strings without pandas' implicit NA vocabulary. Preserve original bytes and per-field `_source` values. Trim text, apply Unicode NFC, and treat empty/`-`/`--`/`n/a`/`na`/`nan`/`null`/`none`/`?`/`unknown` as missing. Parse only complete integer/decimal numeric tokens, with an optional day suffix for `Days`. No digit extraction from arbitrary text, no zero filling and no outcome imputation.

Actual dates use US month/day/year; parse explicitly with `%m/%d/%Y` and accept explicit ISO `%Y-%m-%d`. Unparseable nonmissing values are flagged. Never use locale-dependent automatic date inference. `calculated_days_out` is exclusive, `reported_days_out` remains separate. For this file every reported duration equals exclusive duration + 1, consistent with inclusive endpoints. No original duration is replaced.

Nonnegative integral reported days and matches enter burden summaries. Negative/fractional/unparseable outcomes are excluded only from the corresponding metric; their rows remain in counts and audit exports. Sums use `min_count=1` so an entirely missing group is unavailable rather than zero. Valid sample counts are exported alongside each metric. Durations >365 days and ages outside 12–60 are technical review flags, not automatic deletions or clinical categories.

## Duplicates and club attribution

The primary view excludes exact whole-row duplicate copies only. No exact copies were found in version 2. Candidate duplicates are identical player-name surrogate, case/whitespace-normalized injury label, start and end. Different club/season, age and match-count contexts may reflect transfers or repeated collection. They are retained and separately exported.

The candidate-collapsed sensitivity view keeps the first source row of each complete candidate key, retaining incomplete-key records separately. It is a sensitivity scenario rather than adjudicated truth. No club-specific conclusions use that arbitrary representative. Conflicting games/age/context need source review. Cross-league raw totals therefore must not be interpreted as independent incident events.

## Player identity and histories

`player_id` is a deterministic SHA-256-derived exact normalized-name surrogate, not a verified player identifier. Accents are preserved; different spellings are not merged. Homonyms may be combined. Missing names are omitted from player profiles and have no history features. Source identifiers, birth dates and transfer records are absent.

Sort dated records within a name. History counts include only strictly earlier starts, handling all same-day starts as a batch. Missing onset dates do not enter prior chronological counts. Raw-label recurrence uses case/whitespace-normalized labels; missing labels never constitute a recurrence.

Same-label-after-end repetition additionally requires an earlier valid recorded interval ending strictly before the current onset. This remains a retrospective description; it is not a confirmed reinjury or a population recurrence rate. Left-truncated history, unequal coverage and repeated records affect these counts.

`days_since_previous_injury` is current onset minus the end of the latest-start earlier record. It is unavailable if that preceding onset has tied records or an invalid/missing end. Negative values describe overlap and zero a shared endpoint. It is not confirmed healthy or available time. `overlaps_any_prior_record` checks all earlier valid end dates, so nested intervals cannot hide an earlier long absence. With inclusive dates, onset on the previous end date counts as overlap.

## Burden and date unions

Sum reported days/games by raw injury label, detailed position, recorded age/band, league, season and club. Season is source context, not an allocation of absence days across seasons. Monthly totals assign each episode's entire burden to its onset month. They are not daily occupancy or actual monthly lost days.

The interval-union metric merges valid inclusive [start, end] date intervals within each recorded name before counting dates. It avoids overlap double counting but does not establish medical absence completeness, eligibility or a denominator. It differs deliberately from the sum of episode-days.

Median/IQR and continuous durations lead the severity analysis. All-label rankings retain rare categories and sample sizes. A separate n>=20 descriptive display filter avoids emphasizing tiny categories without removing them from exports. No severe-injury cutoff, hypothesis tests, prediction or survival analysis is used in Milestone 1.

## Descriptive visualization

The burden matrix retains each source label; logarithmic axes reveal rare/long and frequent/short records. Bubble area represents games missed with a small visibility floor. Median reference lines across labels are descriptive, not clinical thresholds. Timelines select the three largest record counts, breaking ties by name; these are illustrative extreme histories, not representative cases. Age summaries are event-weighted, unadjusted and repeatedly sample the same players. No causal claims follow from them.

## Verification and reproducibility

SHA-256 check source bytes before analysis. Keep raw, interim and processed files separate. Export row flags, denominator/sample coverage, duplicate sensitivity and runtime versions. Automated boundary tests cover same-day ordering, future records, inclusive interval unions, missing endpoints and unparseable outcomes. Headline counts/totals are independently reconciled against the source CSV. Notebook outputs are executed against generated tables. Inspect the final figures visually.

The standard bundled Python runtime lacked matplotlib during inspection. The project analysis used the available local Python environment, whose actual versions are captured in `reports/run_manifest.json` and `requirements-lock.txt`. No workbook authoring library is needed; the requested analytical outputs are CSV, Markdown, PNG/SVG and notebooks.

## Public release scope

The completed descriptive study now includes a public bilingual site, an aggregate-only reproducibility package and a targeted literature discussion. Scientific audit supports retaining this descriptive scope: endpoint meaning, clinical episode identity and eligible exposure remain unverified. Survival modeling, prediction and external-data integration require those definitions first; reserved modules contain documentation only. Proposed further work appears in `handoff/future_integration.md`.
