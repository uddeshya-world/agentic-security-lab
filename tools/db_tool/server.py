from tools.base import InvokeResult, is_secure, make_tool_app
from tools.db_tool import queries
from tools.db_tool.schema import get_schema

queries.ensure_seeded()


def _invoke(args: dict) -> InvokeResult:
    table = args.get("table", "")
    if is_secure():
        customer_id = args.get("customer_id")
        if customer_id is None:
            return InvokeResult(
                result={
                    "error": "customer_id required in secure mode",
                    "defense": "SECURE_MODE rejects free-form SQL filter; requires scoped customer_id",
                    "would_have_been_sql": (
                        f"SELECT * FROM {table} WHERE {args.get('filter', '…')}"
                        if args.get("filter")
                        else None
                    ),
                    "secure_sql_template": f"SELECT * FROM {table} WHERE customer_id = ?",
                }
            )
        rows = queries.query_secure(table, int(customer_id))
        return InvokeResult(
            result={
                "rows": rows,
                "count": len(rows),
                "sql": f"SELECT * FROM {table} WHERE customer_id = ?",
                "sql_params": [int(customer_id)],
                "mode": "secure",
            },
            side_effects=[],
        )

    filter_fragment = args.get("filter", "1=1")
    # Build the exact vulnerable SQL the lab will execute (same as queries.query_vulnerable).
    if table not in queries.ALLOWED_TABLES:
        return InvokeResult(result={"error": f"unknown table: {table}"})
    sql = f"SELECT * FROM {table} WHERE {filter_fragment}"
    rows = queries.query_vulnerable(table, filter_fragment)
    return InvokeResult(
        result={
            "rows": rows,
            "count": len(rows),
            "sql": sql,
            "mode": "vulnerable",
            "note": "filter string was concatenated into SQL — classic SQL injection teaching surface",
        },
        side_effects=[],
    )


app = make_tool_app("db_tool", get_schema, _invoke)
