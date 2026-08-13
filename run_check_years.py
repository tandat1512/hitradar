import csv, os
src = r"H:\dự án\DUAN1 github\5.DATA\processed\ml_ready_dataset.csv"
try:
    with open(src, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        years = set()
        for i, row in enumerate(reader):
            if i >= 200000: break
            y = row.get('release_year','').strip()
            if y:
                try: years.add(int(float(y)))
                except: pass
        result = f"min={min(years)}, max={max(years)}, unique_count={len(years)}, years={sorted(years)}"
        print(result)
        with open(r"H:\dự án\DUAN1 github\epic3\feature_3_3\frontend\check_years_result.txt", "w") as out:
            out.write(result)
except Exception as e:
    with open(r"H:\dự án\DUAN1 github\epic3\feature_3_3\frontend\check_years_result.txt", "w") as out:
        out.write(f"ERROR: {e}")
