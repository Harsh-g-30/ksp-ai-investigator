from datetime import datetime
import json
import re


from flask import jsonify, make_response

from prompts.sql_prompt import SQL_SYSTEM_PROMPT
from services.quickml_service import ask_llm
from utils.sql_validator import validate_sql, apply_limit

import logging

logger = logging.getLogger(__name__)


def chat(request, app):
    req_data = request.get_json(silent=True) or {}
    question = req_data.get("question", "").strip()
    if not question:
        return make_response(jsonify({"message": "question is required"}), 400)

    today = datetime.now().strftime("%Y-%m-%d")
    user_turn = f"Current date: {today}\nQuestion: {question}"

    sql = ask_llm(SQL_SYSTEM_PROMPT, user_turn).strip()
    print("\n========== GENERATED SQL ==========")
    print(sql)
    print("===================================\n")
    sql = re.sub(r"^```sql|```$", "", sql, flags=re.IGNORECASE).strip()

    if sql == "NO_QUERY_POSSIBLE":
        return jsonify({
            "answer": "I couldn't map that question to the available crime database fields. Try rephrasing — mention a crime type, district, station, date range, or a name.",
            "sql": None,
            "evidence": [],
        })

    if not validate_sql(sql):
        logger.error(f"Rejected unsafe/non-SELECT SQL: {sql}")
        return make_response(jsonify({"message": "Generated query failed safety checks"}), 400)

    sql = apply_limit(sql)
    sql = re.sub(
        r"COUNT\s*\(\s*\*\s*\)",
        "COUNT(CaseMaster.CaseMasterID)",
        sql,
        flags=re.IGNORECASE,
    )


    sql = re.sub(
        r"COUNT\s*\(\s*\*\s*\)",
        "COUNT(CaseMaster.	CaseMasterID)",
        sql,
        flags=re.IGNORECASE,
    )

    # zcql = app.zcql()
    # try:
    #     rows = zcql.execute_query(sql)  # VERIFY this method name against your SDK version
    # except Exception as e:
    #     logger.error(f"ZCQL execution failed for query [{sql}]: {e}")
    #     return make_response(jsonify({
    #         "message": "Query execution failed. Try narrowing your question (add a date range or specific crime type).",
    #     }), 400)
    zcql = app.zcql()

    try:
        print("\n========== SQL TO EXECUTE ==========")
        print(sql)
        print("====================================\n")

        rows = zcql.execute_query(sql)

    except Exception as e:
        print("\n========== ZCQL EXCEPTION ==========")
        print("SQL:")
        print(sql)
        print("\nException:")
        print(repr(e))
        print("====================================\n")

    logger.exception(f"ZCQL execution failed for query [{sql}]")

    return make_response(jsonify({
        "message": "Query execution failed. Try narrowing your question (add a date range or specific crime type).",
    }), 400)

    summary_prompt = (
        "You are summarizing crime database query results for a police investigator. "
        "Be factual and concise. Cite specific counts/names/dates from the data only. "
        "Do not speculate beyond what's in the rows."
    )
    summary_input = f"Question: {question}\nSQL used: {sql}\nRows returned ({len(rows)}): {json.dumps(rows[:50])}"
    answer = ask_llm(summary_prompt, summary_input)

    logger.info(f"[chat] Q: {question} | SQL: {sql} | rows: {len(rows)}")

    return jsonify({
        "answer": answer,
        "sql": sql,             # shown in UI for the "explainable AI" transparency feature
        "evidence": rows[:50],  # raw rows backing the answer
        "row_count": len(rows),
    })