"""
KSP AI Investigator — Advanced I/O Function (Python)
Routes: POST /chat | GET /case/<id>/summary | GET /analytics/<kind> | GET /network/<accused_name>

NOTE FOR HARSH: This is written against the documented Catalyst Python SDK
patterns (zcatalyst_sdk.initialize(), app.zcql(), app.datastore()). Verify the
exact ZCQL execute method name against your installed zcatalyst-sdk version
(check site-packages/zcatalyst_sdk or run `pip show zcatalyst-sdk` in the
functions/backend folder) before first deploy — SDK method casing has changed
across versions and I can't verify it without your environment.
"""

import os
import sys

# Clear any cached env vars
for key in list(os.environ.keys()):
    if key.startswith('ZOHO_'):
        del os.environ[key]

# Now load fresh
from dotenv import load_dotenv
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.env")), override=True)

print(f"ZOHO_REFRESH_TOKEN loaded: {os.getenv('ZOHO_REFRESH_TOKEN')}")



print(f"ZOHO_CLIENT_ID: {os.getenv('ZOHO_CLIENT_ID')}")
print(f"ZOHO_CLIENT_SECRET: {os.getenv('ZOHO_CLIENT_SECRET')}")
print(f"ZOHO_REFRESH_TOKEN: {os.getenv('ZOHO_REFRESH_TOKEN')}")

# NOW import config
from config import ZOHO_CLIENT_ID, ZOHO_CLIENT_SECRET, ZOHO_REFRESH_TOKEN

import json
import logging
import re
from datetime import datetime, timedelta

import zcatalyst_sdk
from flask import Request, make_response, jsonify

logger = logging.getLogger()

# ---------------------------------------------------------------
# Guardrails for the NL -> SQL chatbot
# ---------------------------------------------------------------
FORBIDDEN_SQL = re.compile(r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE)\b", re.IGNORECASE)
ROW_LIMIT = 200

SQL_SYSTEM_PROMPT = """You are a SQL generator for the Karnataka State Police FIR database.
You ONLY output a single valid SELECT statement. Never output DROP, DELETE,
UPDATE, INSERT, ALTER, or TRUNCATE. Never output more than one statement.
If the question cannot be answered with the schema below, output exactly:
NO_QUERY_POSSIBLE

Schema (tables, key columns, relationships):
CaseMaster(CaseMasterID PK, CrimeNo, CaseNo, CrimeRegisteredDate,
  PolicePersonID FK->Employee, PoliceStationID FK->Unit,
  CaseCategoryID FK->CaseCategory, GravityOffenceID FK->GravityOffence,
  CrimeMajorHeadID FK->CrimeHead, CrimeMinorHeadID FK->CrimeSubHead,
  CaseStatusID FK->CaseStatusMaster, CourtID FK->Court,
  IncidentFromDate, IncidentToDate, latitude, longitude, BriefFacts)
Victim(VictimMasterID PK, CaseMasterID FK, VictimName, AgeYear, GenderID, VictimPolice)
Accused(AccusedMasterID PK, CaseMasterID FK, AccusedName, AgeYear, GenderID, PersonID)
ComplainantDetails(ComplainantID PK, CaseMasterID FK, ComplainantName, AgeYear,
  OccupationID FK->OccupationMaster, ReligionID FK->ReligionMaster, CasteID FK->CasteMaster, GenderID)
ArrestSurrender(ArrestSurrenderID PK, CaseMasterID FK, ArrestSurrenderDate,
  PoliceStationID FK->Unit, IOID FK->Employee, AccusedMasterID FK->Accused)
ChargesheetDetails(CSID PK, CaseMasterID FK, csdate, cstype, PolicePersonID FK->Employee)
ActSectionAssociation(CaseMasterID FK, ActID FK->Act.ActCode, SectionID FK->Section.SectionCode)
Act(ActCode PK, ActDescription, ShortName)
Section(ActCode FK, SectionCode, SectionDescription)
CrimeHead(CrimeHeadID PK, CrimeGroupName)
CrimeSubHead(CrimeSubHeadID PK, CrimeHeadID FK, CrimeHeadName)
CaseCategory(CaseCategoryID PK, LookupValue)
CaseStatusMaster(CaseStatusID PK, CaseStatusName)
GravityOffence(GravityOffenceID PK, LookupValue)
Unit(UnitID PK, UnitName, DistrictID FK, StateID FK)
District(DistrictID PK, DistrictName, StateID FK)
State(StateID PK, StateName)
Employee(EmployeeID PK, FirstName, RankID FK->Rank, DesignationID FK->Designation, UnitID FK, DistrictID FK)
Rank(RankID PK, RankName)
Court(CourtID PK, CourtName, DistrictID FK)

Rules:
- Always JOIN to lookup tables using explicit ON clauses (e.g., ON CaseMaster.CrimeMajorHeadID = CrimeHead.CrimeHeadID).
- Match crime-type phrases against CrimeSubHead.CrimeHeadName using LIKE.
- For "repeat offender" questions, GROUP BY Accused.AccusedName HAVING COUNT(DISTINCT CaseMasterID) > 1.
- Never SELECT * — name columns explicitly.
- Use INNER JOIN for mandatory relationships, LEFT JOIN only when an entity may not exist.
- Return ONLY the SQL, no markdown fences, no explanation.

JOIN Examples (use these patterns):
- CaseMaster to CrimeSubHead: ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.CrimeSubHeadID
- CaseMaster to CrimeHead: ON CaseMaster.CrimeMajorHeadID = CrimeHead.CrimeHeadID
- CaseMaster to Unit: ON CaseMaster.PoliceStationID = Unit.UnitID
- CaseMaster to Employee: ON CaseMaster.PolicePersonID = Employee.EmployeeID
- Accused to CaseMaster: ON Accused.CaseMasterID = CaseMaster.CaseMasterID
- Victim to CaseMaster: ON Victim.CaseMasterID = CaseMaster.CaseMasterID
- CrimeSubHead to CrimeHead: ON CrimeSubHead.CrimeHeadID = CrimeHead.CrimeHeadID
- Unit to District: ON Unit.DistrictID = District.DistrictID
"""


def handler(request: Request):
    try:
        app = zcatalyst_sdk.initialize()
        path, method = request.path, request.method

        if path == "/chat" and method == "POST":
            return chat(request, app)
        # COMMENT OUT BROKEN ENDPOINTS FOR NOW
        # if path.startswith("/case/") and path.endswith("/summary") and method == "GET":
        #     case_id = path.split("/")[2]
        #     return case_summary(case_id, app)
        # if path.startswith("/analytics/") and method == "GET":
        #     kind = path.split("/")[2]
        #     return analytics(kind, app)
        # if path.startswith("/network/") and method == "GET":
        #     name = path.split("/", 2)[2]
        #     return network(name, app)

        return make_response(jsonify({"message": "Route not found"}), 404)

    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        return make_response(jsonify({"message": "Internal server error"}), 500)


# ---------------------------------------------------------------
# /chat — NL question -> SQL -> rows -> NL answer, with evidence
# ---------------------------------------------------------------
def chat(request, app):
    req_data = request.get_json()
    question = (req_data or {}).get("question", "").strip()
    if not question:
        return make_response(jsonify({"message": "question is required"}), 400)

    today = datetime.now().strftime("%Y-%m-%d")
    
    simple_sql_prompt = """Generate a simple SELECT query for the Karnataka Police FIR database.
NO JOINs. NO SELECT *. Use explicit column names only.
Output ONLY the SQL statement.

TABLE MAPPING:
- CaseMaster.CrimeMinorHeadID = CrimeSubHead.CrimeSubHeadID (direct mapping)
- Murder = CrimeSubHeadID 1
- Robbery = CrimeSubHeadID 6
- Theft = CrimeSubHeadID 5
- POCSO Offences = CrimeSubHeadID 14

Examples:
- "How many murder cases" → SELECT COUNT(CaseMasterID) FROM CaseMaster WHERE CrimeMinorHeadID = 1
- "Repeat offenders" → SELECT AccusedName, COUNT(DISTINCT CaseMasterID) FROM Accused GROUP BY AccusedName HAVING COUNT(DISTINCT CaseMasterID) > 1 ORDER BY COUNT(DISTINCT CaseMasterID) DESC LIMIT 50
- "Robbery cases" → SELECT CaseMasterID, CrimeNo FROM CaseMaster WHERE CrimeMinorHeadID = 6 LIMIT 50"""
    
    user_turn = f"Current date: {today}\nQuestion: {question}"
    sql = call_quickml_llm(app, simple_sql_prompt, user_turn, max_tokens=200).strip()
    sql = re.sub(r"^```sql|```$", "", sql, flags=re.IGNORECASE).strip()

    if not sql or sql == "NO_QUERY_POSSIBLE":
        return jsonify({"answer": "I couldn't understand that question.", "sql": None, "evidence": []})

    if not sql.upper().startswith("SELECT"):
        return make_response(jsonify({"message": "Query generation failed"}), 400)

    if "LIMIT" not in sql.upper():
        sql = sql.rstrip(";") + " LIMIT 200"

    zcql = app.zcql()
    try:
        result = zcql.execute_query(sql)
        rows = result if isinstance(result, list) else [result]
    except Exception as e:
        logger.error(f"ZCQL failed: {e}")
        return make_response(jsonify({"message": "Query execution failed"}), 400)

    summary_prompt = "Summarize this crime data result briefly for a police investigator."
    summary_input = f"Question: {question}\nResult: {rows}"
    answer = call_quickml_llm(app, summary_prompt, summary_input, max_tokens=200)

    logger.info(f"[chat] Q: {question} | SQL: {sql} | rows: {len(rows)}")

    return jsonify({
        "answer": answer,
        "sql": sql,
        "evidence": rows[:10],
        "row_count": len(rows),
    })
    
    # Generate simpler SQL without JOINs (use subqueries instead)
    simple_sql_prompt = """You are a SQL generator for the Karnataka State Police FIR database.
CRITICAL: NEVER use SELECT *. You MUST explicitly name every column.

Generate ONLY a simple SELECT query from ONE table — NO JOINs.
Use subqueries if needed. Output ONLY the SQL statement, nothing else.

Examples (study these carefully):
- "How many murder cases?" → SELECT COUNT(*) FROM CaseMaster WHERE CrimeMinorHeadID IN (SELECT CrimeSubHeadID FROM CrimeSubHead WHERE CrimeHeadName LIKE '%murder%')
- "Show repeat offenders" → SELECT AccusedName, COUNT(DISTINCT CaseMasterID) FROM Accused GROUP BY AccusedName HAVING COUNT(DISTINCT CaseMasterID) > 1 LIMIT 50
- "Show murder cases" → SELECT CaseMasterID, CrimeNo FROM CaseMaster WHERE CrimeMinorHeadID IN (SELECT CrimeSubHeadID FROM CrimeSubHead WHERE CrimeHeadName LIKE '%murder%') LIMIT 50

FORBIDDEN: SELECT *, INNER JOIN, LEFT JOIN, any JOIN keyword
REQUIRED: Always name columns, use COUNT(*) for counts only"""
    
    user_turn = f"Current date: {today}\nQuestion: {question}"
    sql = call_quickml_llm(app, simple_sql_prompt, user_turn).strip()
    sql = re.sub(r"^```sql|```$", "", sql, flags=re.IGNORECASE).strip()

    if not sql or sql == "NO_QUERY_POSSIBLE":
        return jsonify({
            "answer": "I couldn't map that question. Try: 'How many murder cases?', 'Show repeat offenders', or 'Cases in 2025'",
            "sql": None,
            "evidence": [],
        })

    if not sql.upper().startswith("SELECT") or FORBIDDEN_SQL.search(sql):
        logger.error(f"Rejected unsafe SQL: {sql}")
        return make_response(jsonify({"message": "Query failed safety checks"}), 400)

    if "LIMIT" not in sql.upper():
        sql = sql.rstrip(";") + f" LIMIT {ROW_LIMIT}"

    zcql = app.zcql()
    try:
        rows = zcql.execute_query(sql)
    except Exception as e:
        logger.error(f"ZCQL execution failed: {e}")
        return make_response(jsonify({"message": "Query execution failed. Try a simpler question."}), 400)

    summary_prompt = (
        "Summarize these crime database results for a police investigator. "
        "Be concise. Cite specific numbers/names/dates only."
    )
    summary_input = f"Question: {question}\nResults: {json.dumps(rows[:30])}"
    answer = call_quickml_llm(app, summary_prompt, summary_input, max_tokens=300)

    logger.info(f"[chat] Q: {question} | rows: {len(rows)}")

    return jsonify({
        "answer": answer,
        "sql": sql,
        "evidence": rows[:30],
        "row_count": len(rows),
    })


# ---------------------------------------------------------------
# /case/<id>/summary — AI case brief: summary, timeline, leads
# ---------------------------------------------------------------
def case_summary(case_id, app):
    zcql = app.zcql()

    case = zcql.execute_query(f"""
        SELECT CaseMaster.CaseMasterID, CaseMaster.CrimeNo, CaseMaster.CrimeRegisteredDate,
               CaseMaster.BriefFacts, CaseMaster.IncidentFromDate, CaseMaster.IncidentToDate,
               CrimeSubHead.CrimeHeadName, CaseStatusMaster.CaseStatusName, Unit.UnitName
        FROM CaseMaster
        JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.CrimeSubHeadID
        JOIN CaseStatusMaster ON CaseMaster.CaseStatusID = CaseStatusMaster.CaseStatusID
        JOIN Unit ON CaseMaster.PoliceStationID = Unit.UnitID
        WHERE CaseMaster.CaseMasterID = {int(case_id)}
    """)
    if not case:
        return make_response(jsonify({"message": "Case not found"}), 404)

    accused = zcql.execute_query(f"SELECT AccusedName, AgeYear, PersonID FROM Accused WHERE CaseMasterID = {int(case_id)}")
    victims = zcql.execute_query(f"SELECT VictimName, AgeYear, GenderID FROM Victim WHERE CaseMasterID = {int(case_id)}")
    arrests = zcql.execute_query(f"SELECT ArrestSurrenderDate, AccusedMasterID FROM ArrestSurrender WHERE CaseMasterID = {int(case_id)}")

    # Repeat-offender / prior-history check for each accused (fuels "suggested leads")
    prior_history = []
    for acc in accused:
        name = acc["AccusedName"]
        prior = zcql.execute_query(f"""
            SELECT CaseMasterID, CrimeNo FROM Accused
            JOIN CaseMaster ON Accused.CaseMasterID = CaseMaster.CaseMasterID
            WHERE AccusedName = '{escape_sql_string(name)}' AND Accused.CaseMasterID != {int(case_id)}
        """)
        if prior:
            prior_history.append({"name": name, "prior_cases": prior})

    prompt = (
        "You are an investigation assistant for Karnataka Police. Given the FIR details, "
        "victims, accused, arrests, and any prior-case history below, produce a JSON object "
        "with keys: summary (2-3 sentences), timeline (array of {date, event}), "
        "persons_involved (array of strings), suggested_leads (array of strings, only if "
        "grounded in the given data — e.g. repeat offender links, unresolved arrests). "
        "Output ONLY valid JSON, no markdown fences."
    )
    context = json.dumps({
        "case": case[0], "accused": accused, "victims": victims,
        "arrests": arrests, "prior_history": prior_history,
    })
    raw = call_quickml_llm(app, prompt, context, max_tokens=700)
    try:
        ai_summary = json.loads(re.sub(r"^```json|```$", "", raw.strip(), flags=re.IGNORECASE).strip())
    except json.JSONDecodeError:
        ai_summary = {"summary": raw, "timeline": [], "persons_involved": [], "suggested_leads": []}

    return jsonify({
        "case": case[0], "accused": accused, "victims": victims, "arrests": arrests,
        "ai_summary": ai_summary,
    })


# ---------------------------------------------------------------
# /analytics/<kind> — dashboard data: trend | hotspots | crimetypes | repeatoffenders
# ---------------------------------------------------------------
def analytics(kind, app):
    zcql = app.zcql()

    if kind == "trend":
        data = zcql.execute_query("""
            SELECT CaseMaster.CrimeRegisteredDate, COUNT(CaseMaster.CaseMasterID) AS cnt
            FROM CaseMaster GROUP BY CaseMaster.CrimeRegisteredDate ORDER BY CaseMaster.CrimeRegisteredDate
        """)
    elif kind == "hotspots":
        data = zcql.execute_query("""
            SELECT Unit.UnitName, CaseMaster.latitude, CaseMaster.longitude, COUNT(CaseMaster.CaseMasterID) AS cnt
            FROM CaseMaster JOIN Unit ON CaseMaster.PoliceStationID = Unit.UnitID
            GROUP BY Unit.UnitName, CaseMaster.latitude, CaseMaster.longitude
            ORDER BY cnt DESC LIMIT 50
        """)
    elif kind == "crimetypes":
        data = zcql.execute_query("""
            SELECT CrimeSubHead.CrimeHeadName, COUNT(CaseMaster.CaseMasterID) AS cnt
            FROM CaseMaster JOIN CrimeSubHead ON CaseMaster.CrimeMinorHeadID = CrimeSubHead.CrimeSubHeadID
            GROUP BY CrimeSubHead.CrimeHeadName ORDER BY cnt DESC
        """)
    elif kind == "repeatoffenders":
        data = zcql.execute_query("""
            SELECT AccusedName, COUNT(DISTINCT CaseMasterID) AS case_count
            FROM Accused GROUP BY AccusedName HAVING COUNT(DISTINCT CaseMasterID) > 1
            ORDER BY case_count DESC LIMIT 50
        """)
    else:
        return make_response(jsonify({"message": f"Unknown analytics kind: {kind}"}), 400)

    return jsonify({"kind": kind, "data": data})


# ---------------------------------------------------------------
# /network/<accused_name> — co-offender graph data for React Flow / Cytoscape
# ---------------------------------------------------------------
def network(name, app):
    zcql = app.zcql()
    name = escape_sql_string(name)

    try:
        # Get all cases where this person is accused
        own_cases_query = f"SELECT CaseMasterID FROM Accused WHERE AccusedName = '{name}' LIMIT 100"
        own_cases = zcql.execute_query(own_cases_query)
        
        if not own_cases or len(own_cases) == 0:
            return jsonify({"nodes": [], "edges": []})

        case_ids = [str(row.get('CaseMasterID', row.get('Accused', {}).get('CaseMasterID'))) for row in own_cases]
        
        if not case_ids:
            return jsonify({"nodes": [], "edges": []})

        case_id_list = ",".join(case_ids)

        # Get co-accused from same cases
        co_accused_query = f"SELECT DISTINCT AccusedName, CaseMasterID FROM Accused WHERE CaseMasterID IN ({case_id_list}) LIMIT 200"
        co_accused = zcql.execute_query(co_accused_query)

        nodes = []
        edges = []
        seen = set()

        # Add primary node
        nodes.append({"id": name, "type": "primary"})

        # Add co-accused nodes and edges
        for row in co_accused:
            # Handle both response formats
            if isinstance(row, dict):
                other = row.get('AccusedName') or (row.get('Accused', {}).get('AccusedName') if isinstance(row.get('Accused'), dict) else row.get('Accused'))
                case_id = row.get('CaseMasterID') or (row.get('Accused', {}).get('CaseMasterID') if isinstance(row.get('Accused'), dict) else None)
            else:
                other = str(row)
                case_id = None

            if other and other != name and other not in seen:
                seen.add(other)
                nodes.append({"id": other, "type": "associate"})
                edges.append({"source": name, "target": other, "via_case": case_id})

        return jsonify({"nodes": nodes, "edges": edges})

    except Exception as e:
        logger.error(f"Network error: {e}")
        return jsonify({"nodes": [], "edges": [], "error": str(e)})


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
def escape_sql_string(value: str) -> str:
    return value.replace("'", "''")


QUICKML_PROJECT_ID = "44972000000032001"
QUICKML_ORG_ID = "60074366475"
QUICKML_CHAT_URL = f"https://api.catalyst.zoho.in/quickml/v1/project/{QUICKML_PROJECT_ID}/glm/chat"
GLM_MODEL_ID = "crm-di-glm47b_30b_it"  # GLM-4.7-Flash, confirmed from console

# Cached in the function's global scope so warm invocations reuse the token
# instead of refreshing on every single call (refresh only ~55 min apart).
_token_cache = {"access_token": None, "expires_at": 0}


def _get_quickml_access_token():
    import os
    import time
    import requests

    # Hardcode for deployment (temporary)
    REFRESH_TOKEN = "1000.2655b1a7219fb8a314545f98a728a662.0f496b7c2aa2e38edb3579a09074aa76"
    CLIENT_ID = "1000.9TZQL2S5ULLXAJL44FGQTHC6V5GCKX"
    CLIENT_SECRET = "ff7db1a0e889134d89b6cb6dc234ae53366c593604"

    if _token_cache["access_token"] and time.time() < _token_cache["expires_at"]:
        return _token_cache["access_token"]

    resp = requests.post("https://accounts.zoho.in/oauth/v2/token", data={
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token",
    }, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    if "access_token" not in data:
        raise Exception(f"OAuth failed: {data}")

    _token_cache["access_token"] = data["access_token"]
    _token_cache["expires_at"] = time.time() + data.get("expires_in", 3600) - 60

    return _token_cache["access_token"]


def call_quickml_llm(app, system_prompt, user_message, max_tokens=400):
    import requests

    token = _get_quickml_access_token()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "CATALYST-ORG": QUICKML_ORG_ID,
    }
    payload = {
        "model": GLM_MODEL_ID,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.2,  # low temperature: we want consistent SQL/JSON, not creative variation
        "stream": False,
        "chat_template_kwargs": {"enable_thinking": False},  # confirmed via test: without this,
        # the model returns its chain-of-thought instead of a direct answer, which breaks SQL/JSON parsing
    }
    resp = requests.post(QUICKML_CHAT_URL, json=payload, headers=headers, timeout=20)
    resp.raise_for_status()
    result = resp.json()
    # Confirmed response shape from live test: {"response": "...", "tool_calls": [...], "usage": {...}}
    if "response" in result:
        return result["response"]
    logger.error(f"Unexpected QuickML response shape: {result}")
    return str(result)