import csv, sys
path = r"H:\dự án\DUAN1 github\5.DATA\processed\ml_ready_dataset.csv"
try:
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        years = set()
        rows = 0
        for i, row in enumerate(reader):
            if i >= 200000: break
            y = row.get('release_year','').strip()
            if y and y.replace('.','',1).lstrip('-').isdigit():
                years.add(int(float(y)))
            rows += 1
        print(f"min_year={min(years)}, max_year={max(years)}, rows_checked={rows}, unique_years={sorted(years)}")
except Exception as e:
    print(f"ERROR: {e}")
