"""
    Titan environment within snowflake
"""

import json

from titan import __version__, connect


def _create_schema(cur, db, schema):
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {db}.{schema}").fetchall()


def _initialize_state(cur, db, schema):
    try:
        cur.execute(
            f"""
            CREATE OR REPLACE FUNCTION {db}.{schema}._TITAN_STATE()
            RETURNS OBJECT
            LANGUAGE SQL
            IMMUTABLE
            AS $$
            SELECT OBJECT_CONSTRUCT()
            $$
            """
        ).fetchall()
    except:
        current_state = json.loads(cur.execute(f"SELECT {db}.{schema}._TITAN_STATE()").fetchone()[0])
        print(current_state)

    #
    try:
        cur.execute(
            rf"""
            CREATE OR REPLACE PROCEDURE {db}.{schema}._TITAN_UPSTATE(key VARCHAR, value VARIANT)
            RETURNS BOOLEAN
            LANGUAGE SQL
            EXECUTE AS CALLER
            AS
            $$
            DECLARE
                new_state VARIANT;
                state_sql VARCHAR;
            BEGIN
                new_state := OBJECT_INSERT(_TITAN_STATE(), :key, :value, TRUE);
                state_sql := 'SELECT TO_OBJECT(PARSE_JSON(\'' || TO_JSON(:new_state) || '\'))';
                EXECUTE IMMEDIATE
                    'CREATE OR REPLACE FUNCTION _TITAN_STATE()
                     RETURNS OBJECT
                     LANGUAGE SQL
                     IMMUTABLE
                     AS \$\$' || :state_sql || '\$\$';
                RETURN TRUE;
            EXCEPTION
                WHEN other THEN
                    return FALSE;
            END;
            $$
            """
        ).fetchall()
    except:
        print("upstate already exists")

    upstate = cur.execute(f"CALL _TITAN_UPSTATE('titan-version', '{__version__}'::VARIANT)").fetchone()[0]
    if not upstate:
        raise Exception("upstate broke")
    cur.execute(f"CALL _TITAN_UPSTATE('installed-packages', [])").fetchone()


def create(db, schema):
    with connect._con() as con:
        with con.cursor() as cur:
            cur.execute(f"USE DATABASE {db}")
            _create_schema(cur, db, schema)
            cur.execute(f"USE SCHEMA {schema}")
            _initialize_state(cur, db, schema)


def get(db, schema):
    with connect._con() as con:
        with con.cursor() as cur:
            cur.execute(f"USE DATABASE {db}")
            cur.execute(f"USE SCHEMA {schema}")
            current_state = json.loads(cur.execute("SELECT _TITAN_STATE()").fetchone()[0])
            print(current_state)
            return current_state
