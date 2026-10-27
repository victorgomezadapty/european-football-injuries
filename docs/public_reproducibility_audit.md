# Public reproducibility audit

Audit date: 27 October 2026. **Result: passed.**

A clean source snapshot was created from Git commit `6655326211657eb0db4301f26d37391a218e9c38` using `git archive HEAD`. It was extracted into a new directory at `publication/repro-check/checkout-6655326`. No existing directory was deleted, moved or overwritten. Tests ran against the archived committed files, rather than the original working tree.

## Checks

| Check | Result |
| --- | --- |
| `npm test` | 5 tests passed; 0 failed |
| `npm run build` | Static site built successfully without raw data, dependency installation or network access |
| Committed public download hashes | All 14 files matched SHA-256 values in `web/downloads/publication_manifest.json` |
| Built download hashes | All 14 corresponding files under `dist/downloads/` matched the same manifest |
| Raw source files | No original raw CSV or source ZIP present under `data/raw/` |
| Named history artifacts | Standardized event files, player profiles, selected timelines, event sequences and row-level review files absent |
| CSV row-level identifiers | No published CSV had a `player_name` or `player_id` header |
| Named-player sample leak check | None of five known source-player names appeared in the audited public text artifacts |
| Public notebook | The included `notebooks/public_review.ipynb` contains aggregate analysis and discussion; it is distinct from the excluded detailed local notebooks |

Git's committed/archived line endings were used for the checksum verification. Every download matched its recorded checksum directly, with no post-check normalization or regeneration needed. The static build preserved these bytes.

The passing web tests cover exact subset median support and total reconciliation, source-versus-candidate meanings, aggregate-only interactive data, bilingual evidence/reference content and required downloads/build entry points. These checks do not constitute independent clinical validation or exhaustive de-identification proof.

## Reproduction boundary

The public presentation can be tested and built from a clean checkout with Node.js 20 or later, using `npm test` followed by `npm run build`. No source injury records are needed for that route.

A new event-level analysis intentionally requires separately obtaining the original credited Kaggle version 2 archive, verifying its registered checksum and following the Python acquisition/analysis instructions. The clean web build is not a claim that raw-data recomputation was performed in this audit.

No implementation, source dataset, publication settings or other project documentation was changed by this audit. The isolated reproduction directory contains only the archived source and its generated build.
