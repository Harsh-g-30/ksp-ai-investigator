import re

FORBIDDEN_SQL = re.compile(
    r"\b(DROP|DELETE|UPDATE|INSERT|ALTER|TRUNCATE)\b",
    re.IGNORECASE
)


def validate_sql(sql: str):
    sql = sql.strip()

    if not sql.upper().startswith("SELECT"):
        return False

    if FORBIDDEN_SQL.search(sql):
        return False

    return True


def apply_limit(sql: str):
    if "LIMIT" not in sql.upper():
        return sql.rstrip(";") + " LIMIT 200"

    return sql