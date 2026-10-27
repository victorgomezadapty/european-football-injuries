# Discussion: recorded injury burden and player availability

This discussion connects the project's descriptive results with twelve selected publications. Published evidence supplies context and methodological standards; it does not medically validate the Kaggle archive. The [search record](literature_search.md) describes a targeted narrative search, not a systematic review. Reference numbers match the [reference registry](../references/references.json).

## 1. The observation unit determines the claim

The file contains 15,603 records, 4,081 recorded player names and 276 absence labels. Injury, illness, quarantine, fitness and rest appear together. The main count is therefore recorded absence-event frequency. The football consensus distinguishes injury definitions, recurrence, severity and exposure; its definitions cannot be assumed from a populated spreadsheet. [Fuller et al., 2006 [1]](https://doi.org/10.1136/bjsm.2005.025270)

The football-specific extension updates injury and illness recording and nomenclature. It supports retaining those distinctions, while leaving vague symptom labels unresolved instead of assigning a tissue diagnosis without evidence. The draft taxonomy is a review aid, not a clinically validated classification. [Waldén et al., 2023 [3]](https://doi.org/10.1136/bjsports-2022-106405)

## 2. Frequent absences and costly absences create different questions

**Hamstring injury** is the most frequent source label: 1,256 records, 52,483 summed reported episode-days and 8,534 summed missed matches. **Cruciate ligament tear** occurs in 226 records but accounts for 56,768 reported episode-days, with a median duration of 230.5 days. These are raw-label summaries, not verified diagnostic groups or individual prognoses.

The burden framework of Bahr and colleagues motivates showing consequence alongside frequency. The project's matrix applies that idea descriptively. Counts, duration and match loss reveal different planning questions; its frequency axis is not an incidence rate, and its median reference lines have no clinical threshold meaning. [Bahr et al., 2018 [4]](https://doi.org/10.1136/bjsports-2017-098160)

## 3. Hamstring prominence has relevant clinical context

The 21-season UEFA cohort used medical-staff injury records and individual exposure. It documented increasing hamstring injury and absence-day proportions. This supports the relevance of examining hamstring consequences, but does not make this archive's raw-label share equivalent to that cohort's clinical categories or exposure-based trends. [Ekstrand et al., 2023 [6]](https://doi.org/10.1136/bjsports-2021-105407)

Earlier prospective medical surveillance also identified substantial muscle-injury consequences and longer absences for clinically defined reinjuries. That supports retaining histories, while emphasizing why a repeated free-text label here cannot establish the same clinical outcome. [Ekstrand et al., 2011 [11]](https://doi.org/10.1177/0363546510395879)

The current data do not demonstrate an epidemic, a workload mechanism or a change in injury incidence.

## 4. Public visibility is selective

Validation by Krutsch and colleagues against team physicians found incorrect diagnoses and missing public/media injury records, with better agreement for some severe types. This shows that public visibility and diagnostic validity can vary by injury type; its results are not a universal correction factor for this file. [Krutsch et al., 2020 [7]](https://doi.org/10.2147/OAJSM.S251081)

Hoenig and colleagues found lower injury recording and a higher severe-injury proportion in a large Transfermarkt archive than in comparator sources. A large public dataset is therefore not necessarily representative. The present Kaggle version's upstream medical verification has not been established independently: this is a relevant analogy, not proof of identical errors. [Hoenig et al., 2022 [8]](https://doi.org/10.1016/j.jsams.2021.11.038)

Structured media surveillance can be useful: Aus der Fünten and colleagues used a defined prospective, multi-source protocol, while acknowledging difficulty identifying minor-injury diagnoses. Downloading an archive does not recreate such collection and exposure procedures. [Aus der Fünten et al., 2023 [9]](https://doi.org/10.1186/s40798-023-00563-x)

Zero missing cells means included records are populated; it does not establish that all injuries, eligible players or accurate diagnoses were captured.

## 5. Repeated intervals affect the headline totals

The primary record-level sum is **563,314 episode-days** and **85,928 missed matches**. No exact whole-row duplicates were found, but 1,973 rows share name surrogate, normalized label and dates with another row. Different club or other context prevents automatically declaring every matching interval a removable duplicate.

The candidate-collapsed sensitivity scenario retains 14,611 records, yielding 532,422 episode-days and 81,226 missed matches: reductions of approximately 5.48% and 5.47%. It keeps the first source row of each complete matching key; it does not adjudicate authoritative club attribution. Both views are published to expose that assumption.

The union of recorded inclusive date intervals avoids overlap double counting within a name, but does not establish complete absence history. Transfers, homonyms and competition-specific match losses still require verification.

## 6. Availability needs a denominator

Hägglund and colleagues observed associations between lower burden, higher match availability and better team performance in a prospectively monitored club cohort. This explains the relevance of availability analytics, without establishing causality or a team-performance effect in this archive. [Hägglund et al., 2013 [5]](https://doi.org/10.1136/bjsports-2013-092215)

Here, **Recorded Availability Burden Profiles** summarize documented consequences. A true availability proportion additionally needs eligible fixtures or observed eligible days, registration intervals and complete absence states. Incidence needs an appropriate exposure denominator. The IOC guidance explains why exposure and consequence measures must match the question; first-to-last-injury time is not a valid substitute. [Bahr et al., 2020 [2]](https://doi.org/10.1136/bjsports-2019-101969)

## 7. An end date is not medical clearance

Every reported duration equals the date difference plus one. Preserving this inclusive convention verifies arithmetic, not clinical endpoint meaning or equivalence to standardized surveillance time loss. Zero-day returns and full-participation definitions require the source protocol.

Return-to-sport guidance distinguishes progression through participation, sport and performance, with multifactorial shared decisions. A recorded interval end supplies none of those assessments. [Ardern et al., 2016 [10]](https://doi.org/10.1136/bjsports-2016-096278)

Repeated labels after recorded endpoints are therefore described as repeated recorded labels, not confirmed clinical reinjuries. Recovery modeling would first require endpoint and observation/censoring verification.

## 8. Calendar patterns generate questions

The monthly chart counts recorded onsets and assigns an episode's entire burden to its onset month. It does not distribute absence dates across months or isolate training-load effects.

A UEFA exposure-based subanalysis found no major overall incidence change during the 2022/23 World Cup season against its historical comparator, with setting-specific nuances. This illustrates why an unusual schedule does not establish its own causal conclusion; it does not show that congestion is harmless everywhere. [Bengtsson et al., 2025 [12]](https://doi.org/10.1136/bmjsem-2025-002772)

## 9. What this project contributes

The reproducible layer makes recorded absence composition, long durations, overlapping histories and sensitivity to repeated episodes explorable. It supports source review and resource-planning questions, not treatment selection, clinical clearance or future injury probabilities. Higher-value next work is identity and episode adjudication, taxonomy and endpoint validation, and complete registration, eligibility and exposure data. Any later onset model must exclude future-known outcomes and full-history totals.

Project-specific values come from `reports/dataset_summary.json` and the burden/sensitivity tables. The separately attributed source is Sanan Muzaffarov's Kaggle dataset. All external claims are linked to publications. No publisher figures, tables, abstracts or long quotations are reproduced.
