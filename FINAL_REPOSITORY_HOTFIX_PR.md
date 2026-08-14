# HitRadar — Final Repository Hotfix

## Summary

- Sanitizes machine-specific paths and usernames across the tracked public tree while retaining pre-sanitization raw evidence only in ignored local storage.
- Removes duplicate root notebooks and unjustified zero-byte placeholders; canonical notebooks remain under `3.NOTEBOOKS/`.
- Stops tracking large processed datasets and runtime model artifacts while preserving the local files and publishing relative-path SHA-256 checksums.
- Restores the three project-management workbooks, three coursework Word documents, SQL-folder guidance, and retrospective notes with non-fabricated provenance labels.
- Regenerates `FINAL_SUBMISSION` as a non-standalone evidence snapshot with manifest integrity, public/private evidence semantics, and current test evidence.
- Leaves Notebook 02 in a clean, password-safe, explicitly not-re-executed state: the hardcoded password fallback and saved failure traceback are removed.
- Hardens repository path detection for ANSI/Jupyter traceback strings, JSON-escaped Windows paths, mixed slashes, and lower-case drive letters; regression tests cover the former false negative.

## Locked artifacts

- Production popularity model: `ffed368b79f5ff221b83fbbe070a1c87a0e474a695a351bb8fbfe18d83bec047`
- Final metrics: `f426407214e0e4ac11b9d4cee8f7c6218a7092216a9d20bec62fe8af37833edf`
- Content recommender: `849d9be06f3338295cfa40ba084014f751203aa7b600d2310a03fcbe390a3ec4`
- KMeans pipeline: `44f99f12bad43f50a8913821360f40aa8c9caec306923a7adb208023909670bc`

Notebook 06 was preserved and was not retrained. The production model and final metrics checksums remain unchanged.

## Validation

- Full Python 3.12 suite: 68 tests, 0 failures, 0 errors, 0 skips.
- `FINAL_SUBMISSION` path scan: 51 text-like files scanned, 0 sensitive matches.
- Current tracked repository path scan: PASS, 0 findings.
- Submission manifest, model checksum, final-metrics checksum, and public/private evidence policy: PASS.
- DOCX files were opened, rendered through Microsoft Word COM, and visually inspected. LibreOffice was unavailable in this environment.
- XLSX files were rendered and inspected; workbook containers and formulas were re-opened successfully.

## Explicit limitation

Notebook 02 was intentionally left in a clean not-re-executed state because PostgreSQL was unavailable in the review environment. Historical PostgreSQL ingestion and validation evidence is retained. No successful Notebook 02 execution is claimed by this PR.

The notebook now reads credentials only from `POSTGRES_PASSWORD` or `PGPASSWORD`; its hardcoded fallback and saved failure traceback were removed. The repository-wide path scanner was hardened and regression-tested against ANSI/Jupyter traceback paths.

## Package semantics

`FINAL_SUBMISSION` is a clean evidence snapshot, not a standalone runnable copy. The canonical repository and locally excluded data/model artifacts listed in `FINAL_SUBMISSION/evidence/external_artifact_checksums.json` are required for full execution. Git history was not rewritten, so legacy commits may still contain historical large artifacts or older path evidence.
