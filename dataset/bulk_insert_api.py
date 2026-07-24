"""
KSP AI Investigator — Bulk CSV Insert via ZCQL API
Reads CSVs and inserts rows into Data Store tables using direct HTTP calls to ZCQL endpoint.
Bypasses the broken CLI import and SDK auth issues.

Run: python3 bulk_insert_api.py
(from your Datathon root folder, where dataset/ exists)
"""
import csv
import os
import sys
import json
import requests
from datetime import datetime

ZCQL_ENDPOINT = "https://api.catalyst.zoho.in/baas/v1/project/44972000000032001/zcql"
CATALYST_ORG = "60074366475"

# Import order (respects FK dependencies)
IMPORT_ORDER = [
    "State", "UnitType", "Rank", "Designation", "CaseCategory", "GravityOffence",
    "CaseStatusMaster", "CrimeHead", "Act", "CasteMaster", "ReligionMaster", "OccupationMaster",
    "District", "CrimeSubHead", "Section",
    "Unit", "Court", "CrimeHeadActSection",
    "Employee",
    "CaseMaster",
    "ComplainantDetails", "Victim", "Accused", "ActSectionAssociation",
    "ArrestSurrender", "ChargesheetDetails",
]

CSV_DIR = "dataset"


def get_access_token():
    """
    Get a fresh OAuth access token using the refresh_token from OAUTH_SETUP.md.
    If this is your first time, follow OAUTH_SETUP.md steps 1-4 first.
    """
    refresh_token = os.environ.get("ZOHO_REFRESH_TOKEN")
    client_id = os.environ.get("ZOHO_CLIENT_ID")
    client_secret = os.environ.get("ZOHO_CLIENT_SECRET")
    
    if not all([refresh_token, client_id, client_secret]):
        print("\nERROR: Missing OAuth credentials!")
        print("Set these environment variables (from OAUTH_SETUP.md step 4):")
        print("  ZOHO_CLIENT_ID")
        print("  ZOHO_CLIENT_SECRET")
        print("  ZOHO_REFRESH_TOKEN")
        print("\nOr paste your access token directly when prompted below.")
        token = input("\nPaste your Zoho OAuth access_token (or 'exit' to quit): ").strip()
        if token.lower() == 'exit':
            sys.exit(1)
        return token
    
    resp = requests.post("https://accounts.zoho.in/oauth/v2/token", data={
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
    }, timeout=10)
    resp.raise_for_status()
    return resp.json()["access_token"]


def load_csv(table_name):
    """Load CSV file for a table, return list of dicts."""
    csv_path = os.path.join(CSV_DIR, f"{table_name}.csv")
    if not os.path.exists(csv_path):
        return []
    
    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned = {}
            for col, val in row.items():
                if val == '' or val is None:
                    continue
                if val.lower() in ('true', '1', 'yes'):
                    cleaned[col] = True
                elif val.lower() in ('false', '0', 'no'):
                    cleaned[col] = False
                else:
                    try:
                        cleaned[col] = int(val)
                    except ValueError:
                        cleaned[col] = val
            rows.append(cleaned)
    return rows


def build_insert_query(table_name, row):
    """Build a single INSERT statement for a row."""
    cols = list(row.keys())
    vals = []
    
    for col, val in row.items():
        if isinstance(val, bool):
            vals.append("true" if val else "false")
        elif isinstance(val, (int, float)):
            vals.append(str(val))
        elif isinstance(val, str):
            escaped = val.replace("'", "''")
            vals.append(f"'{escaped}'")
        else:
            vals.append(f"'{str(val)}'")
    
    col_str = ",".join(cols)
    val_str = ",".join(vals)
    return f"INSERT INTO {table_name} ({col_str}) VALUES ({val_str})"


def execute_zcql(query, access_token):
    """Execute a ZCQL query via the API."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "CATALYST-ORG": CATALYST_ORG,
    }
    payload = {"query": query}
    resp = requests.post(ZCQL_ENDPOINT, json=payload, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


def main():
    print("=" * 70)
    print("KSP AI Investigator — Bulk CSV Insert via ZCQL API")
    print("=" * 70)
    
    print("\nGetting OAuth access token...")
    try:
        access_token = get_access_token()
    except Exception as e:
        print(f"ERROR: Could not get access token: {e}")
        sys.exit(1)
    
    total_inserted = 0
    total_errors = 0
    
    for table_name in IMPORT_ORDER:
        print(f"\n[{table_name}]")
        rows = load_csv(table_name)
        
        if not rows:
            print(f"  No rows to insert (table may not exist yet)")
            continue
        
        inserted = 0
        for i, row in enumerate(rows):
            try:
                query = build_insert_query(table_name, row)
                execute_zcql(query, access_token)
                inserted += 1
                if (i + 1) % 50 == 0:
                    print(f"  ✓ Inserted {i + 1}/{len(rows)} rows...", end='\r')
            except requests.exceptions.HTTPError as e:
                print("\nHTTP ERROR")
                print("Status:", e.response.status_code)

                try:
                    print("Response:", e.response.text)
                except Exception:
                    pass

                raise
                if "does not exist" in str(e) or "404" in str(e):
                    print(f"\n  Table {table_name} does not exist yet, skipping")
                    break
                else:
                    print(f"\n  ✗ Error on row {i + 1}: {e}")
                    total_errors += 1
            except Exception as e:
                print(f"\n  ✗ Error on row {i + 1}: {e}")
                total_errors += 1
        
        if inserted > 0:
            print(f"  ✓ Inserted {inserted}/{len(rows)} rows")
        total_inserted += inserted
    
    print("\n" + "=" * 70)
    print(f"Total inserted: {total_inserted} rows, {total_errors} errors")
    print("=" * 70)
    
    if total_errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()