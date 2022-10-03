CREATE OR REPLACE PROCEDURE titan_reset()
    RETURNS VARIANT
    LANGUAGE PYTHON
    RUNTIME_VERSION = '3.8'
    HANDLER = 'reset'
    PACKAGES = ('snowflake-snowpark-python')
    EXECUTE AS OWNER
AS
$$


def _drop_all_udfs(session, titan_schema):
    funcs = session.sql(f"SHOW USER FUNCTIONS IN SCHEMA {titan_schema}").collect()
    for func in funcs:
        sig = func.arguments.split(" RETURN ")[0]
        session.sql(f"DROP FUNCTION {titan_schema}.{sig}").collect()
        
def _drop_all_sprocs(session, titan_schema):
    sprocs = session.sql(f"SHOW USER PROCEDURES IN SCHEMA {titan_schema}").collect()
    for sproc in sprocs:
        sig = sproc.arguments.split(" RETURN ")[0]
        session.sql(f"DROP PROCEDURE {titan_schema}.{sig}").collect()

def reset(session):
    titan_schema = session.sql("SELECT current_schema()").collect()[0][0]
    if not titan_schema:
        return {"exception": "Missing current schema"}
    # _uninstall_packages(session, titan_schema)
    _drop_all_udfs(session, titan_schema)
    _drop_all_sprocs(session, titan_schema)

    
    return {"success": True}

$$
;