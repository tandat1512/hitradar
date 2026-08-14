# HitRadar Round-4 reproducibility runtime

Fresh-environment validated on 2026-08-14 with Python 3.12.13 (64-bit, Windows). The exact direct dependencies are pinned in `requirements.txt`. `httpx2==2.10.0` was verified through the package index, installed successfully, and exercised by FastAPI/Starlette TestClient, Notebook 07, and the full test suite.

Reproducible setup:

```powershell
py -3.12 -m venv .venv_round4
.\.venv_round4\Scripts\python -m pip install --upgrade pip
.\.venv_round4\Scripts\python -m pip install -r .\5.UNG_DUNG\5.3.config\requirements.txt
.\.venv_round4\Scripts\python -m ipykernel install --user --name hitradar-round4 --display-name "HitRadar Round4 Validation"
jupyter kernelspec list
```

Python 3.12 is required by the pinned NumPy/XGBoost versions. If the Windows
Python launcher is unavailable, replace `py -3.12` with the absolute path to a
Python 3.12 executable.

Canonical project run order remains Notebook 05 → Notebook 06 → Notebook 07. Round 4 executes only Notebook 05 (descriptive audit cleanup) and Notebook 07 (deployment metadata/tests); Notebook 06 is intentionally not retrained. Notebook 05 requires the existing real file `5.DATA/processed/ml_ready_dataset.parquet`; there is deliberately no synthetic-data fallback.

Set `HITRADAR_KERNEL_NAME=hitradar-round4` before using `scratch/execute_notebook.py`. Full install evidence is stored in `5.UNG_DUNG/validation/round4_environment_validation.json` and `round4_environment_install.log`.
