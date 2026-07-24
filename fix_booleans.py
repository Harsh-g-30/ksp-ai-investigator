import os
import csv

DATASET_DIR = "dataset"

# Columns that are Boolean in Catalyst
BOOLEAN_COLUMNS = {
    "Active",
    "VictimPolice",
    "PhysicallyChallenged",
    "IsAccused",
    "IsComplainantAccused",
}

fixed_files = 0

for filename in os.listdir(DATASET_DIR):
    if not filename.endswith(".csv"):
        continue

    path = os.path.join(DATASET_DIR, filename)

    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        headers = reader.fieldnames

    if not headers:
        continue

    changed = False

    for row in rows:
        for col in BOOLEAN_COLUMNS:
            if col not in row:
                continue

            val = row[col].strip().lower()

            if val == "1":
                row[col] = "true"
                changed = True
            elif val == "0":
                row[col] = "false"
                changed = True
            elif val == "":
                row[col] = ""

    if changed:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(rows)

        print(f"✓ Fixed {filename}")
        fixed_files += 1

print(f"\nDone! Updated {fixed_files} CSV files.")