# Public project delivery

Delivery review: 27 October 2026. Analysis source snapshot: 26 October 2026.

## Published destinations

- Interactive Spanish/English website: https://european-football-injuries.vercel.app
- Critical discussion and bibliography: https://european-football-injuries.vercel.app/evidence
- Public source: https://github.com/victorgomezadapty/european-football-injuries
- Derived aggregate dataset: https://www.kaggle.com/datasets/vctorandrsgmezlpez/european-football-injuries-burden-analysis
- Executable public review: https://www.kaggle.com/code/vctorandrsgmezlpez/european-football-injury-burden-review
- Portfolio case study: https://victor-gomez-portfolio.vercel.app/projects/european-football-injuries

The GitHub repository is connected to the Vercel project. The portfolio is published through its existing GitHub/Vercel connection. The source repository includes automated Python and website checks.

## Completed scope and validation

The source audit reconciles 15,603 records, 563,314 summed reported episode-days and 85,928 summed reported missed matches. The candidate repeated-interval sensitivity contains 14,611 rows. These sums can repeat days/matches and are not exposure-based incidence or availability percentages.

The interactive explorer supplies exact precomputed statistics for 36 league/season combinations in each of two views. It includes keyboard selection, accessible tables, Spanish/English text, responsive layouts, animation pause and reduced-motion support. Browser checks cover filters, selections, keyboard navigation, language and motion controls. Production rendering was checked on desktop and mobile. The automated accessibility scan returned zero violations, 46 passes and one incomplete rule requiring manual assessment; this is not a WCAG certification.

Validation includes 13 Python unit tests, five website tests, independent raw-source reconciliation, public-download SHA-256 checks and an executed aggregate-only notebook. A clean committed source snapshot also passed the website tests and build without raw data or dependency installation; see `public_reproducibility_audit.md`. The Kaggle notebook's first published execution completed successfully. Published-version status can be inspected on Kaggle and the latest CI run on GitHub.

The scientific discussion is available in both languages and supported by 12 primary references with verified DOI metadata and BibTeX. The search is documented as a targeted narrative search, not a systematic review. No publisher figures or full articles were redistributed.

## Rights and reproduction

Original creator: Sanan Muzaffarov, European Football Injuries (2020–2025), Kaggle version 2. Source credit, version, checksums, transformations and CC BY-SA 4.0 terms accompany derived aggregate data and figures. Original project source uses MIT. The public Kaggle notebook wrapper displays Apache 2.0; its scope is documented in `NOTEBOOK_LICENSE.md` and does not replace the data license.

The public repository, downloads and Kaggle derivative contain aggregate data and original reproduction materials. The original raw CSV and detailed named histories remain excluded. Event-level reproduction requires obtaining the original credited archive and passing its checksum verification. Source clinical provenance, name identity, endpoint meaning and observation completeness remain unverified. Prediction, incidence, true availability and survival analysis need additional validated inputs and are explicitly outside the supported results.

## Existing portfolio maintenance finding

The portfolio content update passes lint, type checking, static build and project-catalog verification. Its pre-existing Astro 4 dependency tree reports 20 production advisories (8 moderate, 11 high, 1 critical) under `npm audit --omit=dev`. The football site has no runtime or build package dependencies. No framework migration was mixed into the portfolio content update; assessing and updating the existing portfolio dependency tree remains separate maintenance work.
