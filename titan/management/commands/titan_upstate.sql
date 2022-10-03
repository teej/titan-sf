CREATE PROCEDURE titan_upstate(key VARCHAR, value VARIANT)
    RETURNS OBJECT
    LANGUAGE PYTHON
    RUNTIME_VERSION = '3.8'
    HANDLER = 'upstate'
    PACKAGES = ('snowflake-snowpark-python')
    EXECUTE AS OWNER
AS
$$

import json

def upstate(session, key, value):
    new_state = json.loads(session.sql(f"SELECT titan_state()").collect()[0][0])
    new_state[key] = value
    new_state = json.dumps(new_state)

    session.sql(f"""
        CREATE OR REPLACE FUNCTION TITAN_STATE()
            RETURNS OBJECT
            LANGUAGE SQL
            IMMUTABLE
        AS
        'SELECT TO_OBJECT(PARSE_JSON(''{new_state}''))'
    """).collect()
    return {"success": True, "message": f"State updated"}

$$
;



-- $$
-- DECLARE
--     new_state VARIANT;
--     state_sql VARCHAR;
-- BEGIN
--     new_state := OBJECT_INSERT(TITAN_STATE(), :key, :value, TRUE);
--     state_sql := 'SELECT TO_OBJECT(PARSE_JSON('' '|| TO_JSON(:new_state) ||' ''))';
--     EXECUTE IMMEDIATE
--         'CREATE OR REPLACE FUNCTION TITAN_STATE()
--          RETURNS OBJECT
--          LANGUAGE SQL
--          IMMUTABLE
--          AS \$\$' || :state_sql || '\$\$';
--     RETURN TRUE;
-- EXCEPTION
--     WHEN other THEN
--         return FALSE;
-- END;
-- $$

