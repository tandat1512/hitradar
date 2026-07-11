"""
export_ml_ready_dataset.py — Feature 1.8: Export ML-Ready Dataset
HitRadar Pro | EPIC 1 — Data Foundation

Exports analytics.vw_ml_ready_dataset to:
  5.DATA/processed/ml_ready_dataset.csv
  5.DATA/processed/ml_ready_dataset.parquet  (if pyarrow/fastparquet available)

Password: set PGPASSWORD env var (never hardcode).

Usage:
  python 9.SCRIPTS/export_ml_ready_dataset.py [--base-dir PATH]
    [--database DATABASE] [--host HOST] [--port PORT] [--user USER]
"""
import sys
import os
import argparse
from pathlib import Path
from datetime import datetime, timezone

sys.stdout.reconfigure(encoding="utf-8")

try:
    import psycopg2
except ImportError:
    print("ERROR: pip install psycopg2-binary")
    sys.exit(1)

try:
    import pandas as pd
except ImportError:
    print("ERROR: pip install pandas")
    sys.exit(1)

VIEW = "analytics.vw_ml_ready_dataset"
QUERY = f"SELECT * FROM {VIEW}"


def parse_args():
    p = argparse.ArgumentParser(description="HitRadar Feature 1.8 ML-Ready Dataset Export")
    p.add_argument("--host", default="localhost")
    p.add_argument("--port", type=int, default=5432)
    p.add_argument("--user", default="postgres")
    p.add_argument("--database", default="hitradar")
    p.add_argument("--base-dir", dest="base_dir", default=None)
    return p.parse_args()


def resolve_paths(args):
    base = Path(args.base_dir).resolve() if args.base_dir else Path(__file__).resolve().parents[1]
    out_dir = base / "5.DATA" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "ml_ready_dataset.csv"
    parquet_path = out_dir / "ml_ready_dataset.parquet"
    return base, csv_path, parquet_path


def get_conn(args):
    password = os.environ.get("PGPASSWORD")
    if not password:
        print("ERROR: PGPASSWORD not set.")
        sys.exit(1)
    return psycopg2.connect(
        host=args.host, port=args.port, user=args.user,
        password=password, dbname=args.database, connect_timeout=30,
    )


def file_size_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024) if path.exists() else 0.0


def main():
    args = parse_args()
    _, csv_path, parquet_path = resolve_paths(args)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    print(f"=== Feature 1.8 — Export ML-Ready Dataset ===")
    print(f"Time: {now}")
    print(f"Source: {VIEW}")
    print(f"Database: {args.database} @ {args.host}:{args.port}")

    conn = get_conn(args)
    try:
        print("Reading from database (this may take a minute)...")
        df = pd.read_sql(QUERY, conn)
    finally:
        conn.close()

    row_count = len(df)
    col_count = len(df.columns)
    print(f"Rows read: {row_count:,}")
    print(f"Columns: {col_count}")

    df.to_csv(csv_path, index=False)
    print(f"CSV exported: {csv_path}")
    print(f"CSV size: {file_size_mb(csv_path):.2f} MB")

    parquet_ok = False
    parquet_warn = None
    try:
        df.to_parquet(parquet_path, index=False)
        parquet_ok = True
        print(f"Parquet exported: {parquet_path}")
        print(f"Parquet size: {file_size_mb(parquet_path):.2f} MB")
    except ImportError as e:
        parquet_warn = (
            f"WARNING: Parquet export skipped — missing pyarrow/fastparquet ({e}). "
            "CSV export succeeded."
        )
        print(parquet_warn)
    except Exception as e:
        parquet_warn = f"WARNING: Parquet export failed ({e}). CSV export succeeded."
        print(parquet_warn)

    print("\n=== Export Summary ===")
    print(f"  row_count    : {row_count:,}")
    print(f"  column_count : {col_count}")
    print(f"  csv_path     : {csv_path}")
    print(f"  parquet_path : {parquet_path if parquet_ok else 'NOT CREATED'}")
    if parquet_warn:
        print(f"  parquet_note : {parquet_warn}")

    sys.exit(0)


if __name__ == "__main__":
    main()
