# HitRadar hotfix runtime

Validated on 2026-08-13 with Python 3.12.13 (64-bit, Windows). The exact direct dependencies are pinned in `requirements.txt`.

Reproducible setup:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -r .\5.UNG_DUNG\5.3.config\requirements.txt
```

Run notebooks in order: `05_feature_engineering.ipynb`, `06_machine_learning.ipynb`, then `07_ai_deployment.ipynb`. Notebook 05 requires the existing real file `5.DATA/processed/ml_ready_dataset.parquet`; there is deliberately no synthetic-data fallback.
