# European Football Injury Burden — Reproducibility Release

This is an **independent derived analysis**, not the original source dataset. It provides aggregate tables, duplicate-context sensitivity, a bilingual evidence discussion, verified bibliographic metadata and reproducible source code.

## Original data and attribution

Sanan Muzaffarov, [European Football Injuries (2020–2025), Kaggle version 2](https://www.kaggle.com/datasets/sananmuzaffarov/european-football-injuries-2020-2025/versions/2), downloaded 26 October 2026. Source license displayed: **CC BY-SA 4.0**. Derived aggregate statistics/figures preserve that license and credit. [License](https://creativecommons.org/licenses/by-sa/4.0/).

Analysis, code and original design: Víctor Andrés Gómez López, 2026. Original code is MIT; see the separate data-license notice. Transformations: explicit date/duration parsing, quality auditing, label/context aggregation and candidate same-interval collapsing as sensitivity. The original creator does not endorse this analysis. Article findings are cited and paraphrased; no article full text or third-party figures are included.

## What is included

- Aggregate injury-label, league, season and position summaries with sample sizes.
- Original-record and candidate-episode sensitivity views.
- Source schema, methodology, limitations and checksum provenance.
- English/Spanish critical discussion, targeted-search record, DOI bibliography and BibTeX.
- Original code archive and a public review notebook.

The release **does not include the original raw CSV or individual player medical histories**. Obtain the original from its creator to rerun event-level analysis. Raw-file verification prevents accidental source substitution. Python notebook execution needs the project's documented dependencies; the static web build needs only Node 20+.

## Interpretation

The verified original CSV contains 15,603 absence records and 11 columns. Absences include illness, quarantine, fitness/rest and musculoskeletal labels. All durations match inclusive calendar-date counting. 981 candidate repeated-interval groups span clubs; keeping one row per matching name, label and dates produces a 14,611-row sensitivity view. This is not adjudication of clinically independent episodes.

Frequency, severity and cumulative burden are distinct. These records do not supply healthy-player exposure, eligible-fixture denominators or verified observation windows. No injury incidence rate, player availability percentage, clinical recovery forecast or prospective injury-risk prediction is provided. Clinical provenance and medical endpoint meaning remain unverified. Zero blank values does not establish complete injury surveillance.

## Project

- [Interactive bilingual study](https://european-football-injuries.vercel.app)
- [GitHub and reproduction instructions](https://github.com/victorgomezadapty/european-football-injuries)
- [Scientific discussion](https://european-football-injuries.vercel.app/evidence)
- [Author portfolio](https://victor-gomez-portfolio.vercel.app)
