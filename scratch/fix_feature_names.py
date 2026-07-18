import json
from pathlib import Path

prep_dir = Path('7.ML/7.5.preprocessing')
encoder_cats = json.loads((prep_dir / 'encoder_categories.json').read_text())

num_cols = ['duration_min', 'release_year', 'danceability', 'energy', 'loudness', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']

candidates = {
    'p22_a': {'cat_drop': 'first', 'missing_indicator': False},
    'p22_b': {'cat_drop': 'first', 'missing_indicator': True},
    'p22_c': {'cat_drop': 'none', 'missing_indicator': True},
    'p22_d': {'cat_drop': None, 'missing_indicator': False}
}

for dir_id, cfg in candidates.items():
    feat_names = []
    
    # 1. Numerical features (same for all)
    feat_names.extend(num_cols)
    
    # 2. Missing Indicator for numerical features
    if cfg['missing_indicator']:
        # Only tempo has missing values in the numerical cols
        feat_names.append('tempo_missing_indicator')
        
    # 3. Categorical features
    cid_upper = dir_id.upper().replace('_', '-') # p22_a -> P22-A
    if cfg['cat_drop'] is not None:
        for cat in encoder_cats:
            if cat['candidate_id'] == cid_upper:
                col = cat['column']
                categories = cat['categories']
                
                # simulate OneHotEncoder(drop)
                if cfg['cat_drop'] == 'first':
                    # Drop the first category if it exists
                    out_cats = categories[1:] if len(categories) > 0 else []
                else:
                    out_cats = categories
                
                for c_val in out_cats:
                    feat_names.append(f"{col}_{c_val}")
                    
    # Write feature_names.json
    p = prep_dir / dir_id / 'feature_names.json'
    if p.exists() or dir_id != 'p22_d': # just to be safe
        p.write_text(json.dumps(feat_names, indent=2))
        
    # Also update output_schema.json to match exactly
    out_schema_path = prep_dir / dir_id / 'output_schema.json'
    if out_schema_path.exists():
        schema = json.loads(out_schema_path.read_text())
        schema['output_feature_count'] = len(feat_names)
        out_schema_path.write_text(json.dumps(schema, indent=2))
        
    print(f"{dir_id} ({cid_upper}) -> {len(feat_names)} features")
