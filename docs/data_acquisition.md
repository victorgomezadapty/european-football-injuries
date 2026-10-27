# Data acquisition and provenance

Official source: Sanan Muzaffarov, [European Football Injuries (2020–2025)](https://www.kaggle.com/datasets/sananmuzaffarov/european-football-injuries-2020-2025).

1. Open the official Kaggle page and select **version 2** in version history. The page displayed version 2 on 2026-10-26.
2. Sign in if required. Choose **Download → Download dataset as zip**. Download the whole dataset, not the currently selected columns: the explorer initially hides one of the 11 columns.
3. Register the original archive with `python scripts/acquire_data.py --archive "C:\path\archive.zip"`.
4. The script safely extracts CSV bytes, records SHA-256 hashes and refuses to replace an existing different raw file. `python scripts/acquire_data.py` subsequently checks the registered files without another download.
5. Run `python -m src.pipeline --as-of 2026-10-26`.

The script can attempt the public Kaggle download endpoint when no archive/manifest exists. In this environment that endpoint returned HTTP 404, so the actual acquisition used the official page in the user's signed-in in-app browser. No credentials were exported or saved in this repository.

The downloaded archive contains `full_dataset_thesis - 1.csv` (1,600,846 bytes). The ZIP is retained as `data/raw/kaggle_version_2.zip`. The manifest is the authoritative checksum record. Raw and row-level derived data are ignored by Git by default. Aggregate outputs and the manifest remain available for portfolio review.

Attribution: Sanan Muzaffarov, dataset license displayed as [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Changes: typed derivatives, audits and descriptive summaries, with original bytes preserved. DOI in the brief: `10.34740/KAGGLE/DSV/14465228`, version association not independently verified. Dataset documentation describes a thesis collection; the original collection and return-to-play definitions remain to be verified.
