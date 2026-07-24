"""
KSP AI Investigator — Synthetic Dataset Generator
Generates CSVs for every table in schema.sql, ready to import into Catalyst Data Store.

Run: python3 generate_seed_data.py
Output: ./output/*.csv  (one file per table)
"""
import csv
import os
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker("en_IN")
random.seed(42)
Faker.seed(42)

OUT = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(OUT, exist_ok=True)

def write_csv(name, header, rows):
    with open(os.path.join(OUT, f"{name}.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)
    print(f"  {name}.csv  -> {len(rows)} rows")

# ---------------------------------------------------------------
# 1. Geography: State -> District -> Unit (police station)
# ---------------------------------------------------------------
states = [(1, "Karnataka", 1, 1)]
write_csv("State", ["StateID", "StateName", "NationalityID", "Active"], states)

district_names = [
    "Bengaluru Urban", "Bengaluru Rural", "Mysuru", "Belagavi",
    "Ballari", "Dakshina Kannada", "Kalaburagi", "Tumakuru",
    "Shivamogga", "Hubballi-Dharwad",
]
districts = [(i + 1, name, 1, 1) for i, name in enumerate(district_names)]
write_csv("District", ["DistrictID", "DistrictName", "StateID", "Active"], districts)

unit_types = [
    (1, "Police Station", "City", 4, 1),
    (2, "Circle Office", "District", 3, 1),
    (3, "Sub-Division", "District", 2, 1),
    (4, "District HQ", "District", 1, 1),
]
write_csv("UnitType", ["UnitTypeID", "UnitTypeName", "CityDistState", "Hierarchy", "Active"], unit_types)

station_suffixes = ["Town", "Rural", "Traffic", "Central", "East", "West", "North", "South", "CEN Crime", "Cyber Crime"]
units = []
unit_id = 1
for d_id, d_name in enumerate(district_names, start=1):
    n_stations = random.randint(3, 5)
    for _ in range(n_stations):
        suffix = random.choice(station_suffixes)
        units.append((
            unit_id,
            f"{d_name.split()[0]} {suffix} PS",
            1,           # UnitTypeID = Police Station
            None,        # ParentUnit
            1,           # NationalityID
            1,           # StateID
            d_id,        # DistrictID
            1,           # Active
        ))
        unit_id += 1
write_csv("Unit", ["UnitID", "UnitName", "TypeID", "ParentUnit", "NationalityID", "StateID", "DistrictID", "Active"], units)

# ---------------------------------------------------------------
# 2. Employees (police officers)
# ---------------------------------------------------------------
ranks = [
    (1, "Constable", 6, 1), (2, "Head Constable", 5, 1), (3, "ASI", 4, 1),
    (4, "SI", 3, 1), (5, "Inspector", 2, 1), (6, "DSP", 1, 1),
]
write_csv("Rank", ["RankID", "RankName", "Hierarchy", "Active"], ranks)

designations = [
    (1, "Investigating Officer", 1, 1), (2, "SHO", 1, 2),
    (3, "Beat Officer", 1, 3), (4, "Reporting Officer", 1, 4),
]
write_csv("Designation", ["DesignationID", "DesignationName", "Active", "SortOrder"], designations)

employees = []
for eid in range(1, 121):
    unit = random.choice(units)
    dob = fake.date_of_birth(minimum_age=25, maximum_age=55)
    appt = dob + timedelta(days=random.randint(365 * 22, 365 * 30))
    employees.append((
        eid, unit[6], unit[0], random.randint(1, 6), random.randint(1, 4),
        f"KGID{100000 + eid}", fake.first_name_male() if random.random() > 0.15 else fake.first_name_female(),
        dob.isoformat(), random.choice([1, 2]), random.randint(1, 8),
        0, appt.isoformat(),
    ))
write_csv("Employee", [
    "EmployeeID", "DistrictID", "UnitID", "RankID", "DesignationID", "KGID", "FirstName",
    "EmployeeDOB", "GenderID", "BloodGroupID", "PhysicallyChallenged", "AppointmentDate",
], employees)

# ---------------------------------------------------------------
# 3. Courts
# ---------------------------------------------------------------
courts = []
for i, (d_id, d_name) in enumerate(zip(range(1, len(district_names) + 1), district_names), start=1):
    courts.append((i, f"District & Sessions Court, {d_name}", d_id, 1, 1))
write_csv("Court", ["CourtID", "CourtName", "DistrictID", "StateID", "Active"], courts)

# ---------------------------------------------------------------
# 4. Crime classification masters
# ---------------------------------------------------------------
case_categories = [(1, "FIR"), (2, "UDR"), (3, "Zero FIR"), (4, "PAR")]
write_csv("CaseCategory", ["CaseCategoryID", "LookupValue"], case_categories)

gravity = [(1, "Heinous"), (2, "Non-Heinous")]
write_csv("GravityOffence", ["GravityOffenceID", "LookupValue"], gravity)

case_status = [
    (1, "Under Investigation"), (2, "Charge Sheeted"), (3, "Closed"),
    (4, "Undetected"), (5, "False Case"), (6, "Acquitted"), (7, "Convicted"),
]
write_csv("CaseStatusMaster", ["CaseStatusID", "CaseStatusName"], case_status)

crime_heads = [
    (1, "Crimes Against Body"), (2, "Crimes Against Property"),
    (3, "Crimes Against Women"), (4, "Crimes Against Children"),
    (5, "Cyber Crime"), (6, "Narcotics"), (7, "Economic Offences"),
    (8, "Public Order Offences"),
]
write_csv("CrimeHead", ["CrimeHeadID", "CrimeGroupName", "Active"], [(a, b, 1) for a, b in crime_heads])

crime_subheads_raw = {
    1: ["Murder", "Attempt to Murder", "Grievous Hurt", "Assault"],
    2: ["Theft", "Robbery", "Burglary", "Dacoity", "Criminal Trespass"],
    3: ["Dowry Harassment", "Molestation", "Domestic Violence", "Stalking"],
    4: ["POCSO Offences", "Child Trafficking", "Child Labour"],
    5: ["Online Financial Fraud", "Hacking", "Cyberstalking", "Identity Theft"],
    6: ["NDPS - Possession", "NDPS - Trafficking"],
    7: ["Cheating", "Criminal Breach of Trust", "Forgery"],
    8: ["Rioting", "Unlawful Assembly"],
}
crime_subheads = []
sub_id = 1
for head_id, names in crime_subheads_raw.items():
    for seq, name in enumerate(names, start=1):
        crime_subheads.append((sub_id, head_id, name, seq))
        sub_id += 1
write_csv("CrimeSubHead", ["CrimeSubHeadID", "CrimeHeadID", "CrimeHeadName", "SeqID"], crime_subheads)

acts = [
    ("IPC", "Indian Penal Code, 1860", "IPC", 1),
    ("POCSO", "Protection of Children from Sexual Offences Act, 2012", "POCSO", 1),
    ("NDPS", "Narcotic Drugs and Psychotropic Substances Act, 1985", "NDPS", 1),
    ("ITACT", "Information Technology Act, 2000", "IT Act", 1),
    ("MVACT", "Motor Vehicles Act, 1988", "MV Act", 1),
]
write_csv("Act", ["ActCode", "ActDescription", "ShortName", "Active"], acts)

sections = [
    ("IPC", "302", "Punishment for murder", 1),
    ("IPC", "307", "Attempt to murder", 1),
    ("IPC", "323", "Voluntarily causing hurt", 1),
    ("IPC", "354", "Assault on woman with intent to outrage modesty", 1),
    ("IPC", "379", "Theft", 1),
    ("IPC", "392", "Robbery", 1),
    ("IPC", "420", "Cheating and dishonestly inducing delivery of property", 1),
    ("IPC", "406", "Criminal breach of trust", 1),
    ("IPC", "498A", "Husband or relative subjecting woman to cruelty", 1),
    ("IPC", "506", "Criminal intimidation", 1),
    ("POCSO", "4", "Punishment for penetrative sexual assault", 1),
    ("POCSO", "8", "Punishment for sexual assault", 1),
    ("NDPS", "20", "Punishment for contravention involving cannabis", 1),
    ("NDPS", "22", "Punishment for offences involving psychotropic substances", 1),
    ("ITACT", "66", "Computer related offences", 1),
    ("ITACT", "66C", "Identity theft", 1),
    ("ITACT", "66D", "Cheating by personation using computer resource", 1),
    ("MVACT", "184", "Dangerous driving", 1),
]
sections_with_key = [(f"{act}_{sec}", act, sec, desc, active) for act, sec, desc, active in sections]
write_csv("Section", ["SectionRowKey", "ActCode", "SectionCode", "SectionDescription", "Active"], sections_with_key)

# Map crime sub-head groups to plausible act/sections (simplified heuristic mapping)
subhead_to_sections = {
    "Murder": [("IPC", "302")], "Attempt to Murder": [("IPC", "307")],
    "Grievous Hurt": [("IPC", "323")], "Assault": [("IPC", "323"), ("IPC", "354")],
    "Theft": [("IPC", "379")], "Robbery": [("IPC", "392")], "Burglary": [("IPC", "379")],
    "Dacoity": [("IPC", "392")], "Criminal Trespass": [("IPC", "379")],
    "Dowry Harassment": [("IPC", "498A")], "Molestation": [("IPC", "354")],
    "Domestic Violence": [("IPC", "498A")], "Stalking": [("IPC", "354"), ("IPC", "506")],
    "POCSO Offences": [("POCSO", "4"), ("POCSO", "8")],
    "Child Trafficking": [("IPC", "420")], "Child Labour": [("IPC", "420")],
    "Online Financial Fraud": [("ITACT", "66D"), ("IPC", "420")],
    "Hacking": [("ITACT", "66")], "Cyberstalking": [("ITACT", "66"), ("IPC", "506")],
    "Identity Theft": [("ITACT", "66C")],
    "NDPS - Possession": [("NDPS", "20")], "NDPS - Trafficking": [("NDPS", "22")],
    "Cheating": [("IPC", "420")], "Criminal Breach of Trust": [("IPC", "406")],
    "Forgery": [("IPC", "420")], "Rioting": [("IPC", "506")], "Unlawful Assembly": [("IPC", "506")],
}

crime_head_act_section = []
seen_chas = set()
for sh_id, head_id, name, seq in crime_subheads:
    for act, sec in subhead_to_sections.get(name, [("IPC", "420")]):
        key = f"{head_id}_{act}_{sec}"
        if key not in seen_chas:  # avoid duplicate rows across sub-heads sharing the same head+act+section
            seen_chas.add(key)
            crime_head_act_section.append((key, head_id, act, sec))
write_csv("CrimeHeadActSection", ["RowKey", "CrimeHeadID", "ActCode", "SectionCode"], crime_head_act_section)

castes = [(1, "General"), (2, "OBC"), (3, "SC"), (4, "ST"), (5, "Minority")]
write_csv("CasteMaster", ["caste_master_id", "caste_master_name"], castes)

religions = [(1, "Hindu"), (2, "Muslim"), (3, "Christian"), (4, "Sikh"), (5, "Other")]
write_csv("ReligionMaster", ["ReligionID", "ReligionName"], religions)

occupations = [
    (1, "Farmer"), (2, "Daily Wage Labourer"), (3, "Government Employee"),
    (4, "Private Employee"), (5, "Business/Self-Employed"), (6, "Student"),
    (7, "Unemployed"), (8, "Homemaker"),
]
write_csv("OccupationMaster", ["OccupationID", "OccupationName"], occupations)

# ---------------------------------------------------------------
# 5. Repeat-offender pool (so the network-graph & profiling features have real signal)
# ---------------------------------------------------------------
NUM_REPEAT_OFFENDERS = 35
repeat_offender_names = [fake.name_male() for _ in range(NUM_REPEAT_OFFENDERS)]
# a handful of "gangs" — small cliques of offenders who co-appear across multiple FIRs
gangs = [random.sample(repeat_offender_names, k=random.randint(2, 4)) for _ in range(8)]

# ---------------------------------------------------------------
# 6. Cases + related child records
# ---------------------------------------------------------------
NUM_CASES = 450
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2026, 7, 1)

case_master, complainants, act_section_assoc = [], [], []
victims, accused, arrests, chargesheets = [], [], [], []

complainant_id = accused_id = victim_id = arrest_id = cs_id = 1
running_serials = {}  # (unit_id, category_id, year) -> serial counter

for case_id in range(1, NUM_CASES + 1):
    unit = random.choice(units)
    unit_id, district_id = unit[0], unit[6]
    reg_date = fake.date_time_between(start_date=START_DATE, end_date=END_DATE)
    year = reg_date.year
    category_id = random.choices([1, 2, 3, 4], weights=[0.75, 0.1, 0.1, 0.05])[0]

    key = (unit_id, category_id, year)
    running_serials[key] = running_serials.get(key, 0) + 1
    serial = running_serials[key]

    crime_no = f"1{district_id:04d}{unit_id:04d}{year}{serial:05d}"
    case_no = f"{year}{serial:05d}"

    crime_head_id = random.randint(1, 8)
    subheads_for_head = [s for s in crime_subheads if s[1] == crime_head_id]
    subhead = random.choice(subheads_for_head)

    gravity_id = 1 if subhead[2] in ("Murder", "Attempt to Murder", "Robbery", "Dacoity", "POCSO Offences") else 2
    status_id = random.choices([1, 2, 3, 4, 5, 6, 7], weights=[0.35, 0.25, 0.1, 0.1, 0.05, 0.05, 0.1])[0]

    incident_start = reg_date - timedelta(hours=random.randint(1, 72))
    info_received = incident_start + timedelta(hours=random.randint(1, 24))

    # Bengaluru-ish lat/long jittered per district for demo heatmaps
    base_lat, base_lng = 12.9716 + district_id * 0.15, 77.5946 + district_id * 0.1
    lat = round(base_lat + random.uniform(-0.05, 0.05), 6)
    lng = round(base_lng + random.uniform(-0.05, 0.05), 6)

    officer = random.choice(employees)
    court = random.choice(courts)

    case_master.append((
        case_id, crime_no, case_no, reg_date.date().isoformat(),
        officer[0], unit_id, category_id, gravity_id, crime_head_id, subhead[0],
        status_id, court[0],
        incident_start.isoformat(), reg_date.isoformat(), info_received.isoformat(),
        lat, lng,
        f"On {incident_start.strftime('%d-%b-%Y')}, a case of {subhead[2].lower()} was reported "
        f"near {unit[1]}. Investigation initiated under {crime_no}.",
    ))

    # Act/Section
    mapped = [x for x in crime_head_act_section if x[1] == crime_head_id]
    if mapped:
        for order, (key, h, act_code, sec_code) in enumerate(random.sample(mapped, k=min(len(mapped), random.randint(1, 2))), start=1):
            row_key = f"{case_id}_{act_code}_{sec_code}"
            act_section_assoc.append((row_key, case_id, act_code, sec_code, order, order))

    # Complainant
    complainants.append((
        complainant_id, case_id, fake.name(), random.randint(19, 70),
        random.randint(1, 8), random.randint(1, 5), random.randint(1, 5), random.choice([1, 2]),
    ))
    complainant_id += 1

    # Victims (1-3)
    for _ in range(random.randint(1, 3)):
        victims.append((
            victim_id, case_id, fake.name(), random.randint(5, 75),
            random.choice(["M", "F", "T"]), 0,
        ))
        victim_id += 1

    # Accused (1-4), with ~20% chance of pulling from the repeat-offender / gang pool
    n_accused = random.randint(1, 4)
    use_gang = random.random() < 0.2
    if use_gang:
        gang = random.choice(gangs)
        names_for_case = gang[:n_accused] if len(gang) >= n_accused else gang + [fake.name_male() for _ in range(n_accused - len(gang))]
    elif random.random() < 0.15:
        names_for_case = random.sample(repeat_offender_names, k=min(n_accused, len(repeat_offender_names)))
    else:
        names_for_case = [fake.name() for _ in range(n_accused)]

    case_accused_ids = []
    for idx, name in enumerate(names_for_case, start=1):
        accused.append((
            accused_id, case_id, name, random.randint(18, 60),
            random.choice(["M", "F", "T"]), f"A{idx}",
        ))
        case_accused_ids.append(accused_id)
        accused_id += 1

    # Arrests (some accused get arrested)
    for acc_id in case_accused_ids:
        if random.random() < 0.6:
            io = random.choice(employees)
            arrests.append((
                arrest_id, case_id, random.choice([1, 2]),
                (reg_date + timedelta(days=random.randint(0, 30))).date().isoformat(),
                1, district_id, unit_id, io[0], court[0], acc_id, 1, 0,
            ))
            arrest_id += 1

    # Chargesheet (only for older, resolved-ish cases)
    if status_id in (2, 5, 6, 7) or (year < 2026 and random.random() < 0.5):
        chargesheets.append((
            cs_id, case_id,
            (reg_date + timedelta(days=random.randint(30, 120))).isoformat(),
            random.choices(["A", "B", "C"], weights=[0.7, 0.15, 0.15])[0],
            officer[0],
        ))
        cs_id += 1

write_csv("CaseMaster", [
    "CaseMasterID", "CrimeNo", "CaseNo", "CrimeRegisteredDate", "PolicePersonID", "PoliceStationID",
    "CaseCategoryID", "GravityOffenceID", "CrimeMajorHeadID", "CrimeMinorHeadID", "CaseStatusID", "CourtID",
    "IncidentFromDate", "IncidentToDate", "InfoReceivedPSDate", "latitude", "longitude", "BriefFacts",
], case_master)

write_csv("ComplainantDetails", [
    "ComplainantID", "CaseMasterID", "ComplainantName", "AgeYear", "OccupationID", "ReligionID", "CasteID", "GenderID",
], complainants)

write_csv("ActSectionAssociation", ["RowKey", "CaseMasterID", "ActID", "SectionID", "ActOrderID", "SectionOrderID"], act_section_assoc)
write_csv("Victim", ["VictimMasterID", "CaseMasterID", "VictimName", "AgeYear", "GenderID", "VictimPolice"], victims)
write_csv("Accused", ["AccusedMasterID", "CaseMasterID", "AccusedName", "AgeYear", "GenderID", "PersonID"], accused)
write_csv("ArrestSurrender", [
    "ArrestSurrenderID", "CaseMasterID", "ArrestSurrenderTypeID", "ArrestSurrenderDate",
    "ArrestSurrenderStateId", "ArrestSurrenderDistrictId", "PoliceStationID", "IOID", "CourtID",
    "AccusedMasterID", "IsAccused", "IsComplainantAccused",
], arrests)
write_csv("ChargesheetDetails", ["CSID", "CaseMasterID", "csdate", "cstype", "PolicePersonID"], chargesheets)

print(f"\nDone. {NUM_CASES} cases generated in {OUT}/")
print(f"Repeat offender pool: {NUM_REPEAT_OFFENDERS} names, {len(gangs)} clique groups embedded across cases.")
