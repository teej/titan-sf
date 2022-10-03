CREATE FUNCTION titan_state()
    RETURNS OBJECT
    LANGUAGE SQL
    IMMUTABLE
AS $$
SELECT OBJECT_CONSTRUCT()
$$
;

CREATE FUNCTION titan_packages()
    RETURNS ARRAY
    LANGUAGE SQL
AS
$$
SELECT titan_state():packages::ARRAY
$$
;

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


CREATE PROCEDURE titan_state_del(key VARCHAR)
    RETURNS OBJECT
    LANGUAGE PYTHON
    RUNTIME_VERSION = '3.8'
    HANDLER = 'state_del'
    PACKAGES = ('snowflake-snowpark-python')
    EXECUTE AS OWNER
AS
$$

import json

def state_del(session, key):
    new_state = json.loads(session.sql("SELECT titan_state()").collect()[0][0])
    del new_state[key]
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


CREATE PROCEDURE titan_state_append(key VARCHAR, value VARIANT)
    RETURNS OBJECT
    LANGUAGE PYTHON
    RUNTIME_VERSION = '3.8'
    HANDLER = 'state_append'
    PACKAGES = ('snowflake-snowpark-python')
    EXECUTE AS OWNER
AS
$$

import json

def state_append(session, key, value):
    new_state = json.loads(session.sql(f"SELECT titan_state():{key}").collect()[0][0])
    new_state.append(value)
    return json.loads(session.call('titan_upstate', key, new_state))
$$
;


CREATE PROCEDURE titan_state_remove(key VARCHAR, value VARIANT)
    RETURNS OBJECT
    LANGUAGE PYTHON
    RUNTIME_VERSION = '3.8'
    HANDLER = 'state_remove'
    PACKAGES = ('snowflake-snowpark-python')
    EXECUTE AS OWNER
AS
$$

import json

def state_remove(session, key, value):
    new_state = json.loads(session.sql(f"SELECT titan_state():{key}").collect()[0][0])
    new_state.remove(value)
    return json.loads(session.call('titan_upstate', key, new_state))

$$
;
