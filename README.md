# HitRadar / HitRadar Pro

The current canonical handoff is under `FINAL_SUBMISSION/`. Run notebooks in
order: Notebook 05 → Notebook 06 → Notebook 07.

Temporal governance remains `release_year <= 2017` for selection train, 2018
for validation, `<2019` for final refit, and `>=2019` for the final temporal
holdout. The corrected Round-2 pipeline did not use the 2019+ horizon for
winner selection, but that same horizon had been inspected during an earlier
development iteration.

Deployment allows post-2020 predictions with an explicit temporal-
extrapolation warning. See `FINAL_SUBMISSION/README_FINAL_SUBMISSION.md` for
setup commands, evidence, limitations, and the submission manifest.
