import json

with open('E:\\Dự án 1 hitrada\\hitradar\\7.ML\\7.7.model_training\\registries\\experiment_registry.json', 'r') as f:
    data = json.load(f)

# Deduplicate based on 'timestamp' and 'experiment_id' + 'fold_id'
seen = set()
dedup = []
for d in data:
    # Use a generic hash to deduplicate
    h = json.dumps(d, sort_keys=True)
    if h not in seen:
        seen.add(h)
        dedup.append(d)

# Wait, if there are exact duplicates, this removes them.
# What if it's the same experiment_id but different timestamp?
# I'll just keep the LAST occurrence for each stage/fold of the same experiment_id
final_data = {}
for d in data:
    key = (d.get('experiment_id'), d.get('stage'), d.get('fold_id'), d.get('config_id'))
    final_data[key] = d

with open('E:\\Dự án 1 hitrada\\hitradar\\7.ML\\7.7.model_training\\registries\\experiment_registry.json', 'w') as f:
    json.dump(list(final_data.values()), f, indent=2)

print("Deduped registry to", len(final_data), "records")
