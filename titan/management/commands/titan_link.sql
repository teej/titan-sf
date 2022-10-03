CREATE PROCEDURE titan_link(from_name VARCHAR, to_name VARCHAR, arguments ARRAY, returns VARCHAR)
    RETURNS OBJECT
    LANGUAGE PYTHON
    RUNTIME_VERSION = '3.8'
    HANDLER = 'link'
    PACKAGES = ('snowflake-snowpark-python')
    EXECUTE AS OWNER
AS
$$

def link(session, from_name, to_name, arguments, returns):
    titan_schema = session.sql("SELECT current_schema()").collect()[0][0];
    if not titan_schema:
        return {"success": False, "exception": "Missing current schema"}

    full_sig = ", ".join([" ".join(arg) for arg in arguments])
    name_sig = ", ".join([arg[0] for arg in arguments])
    type_sig = ", ".join([arg[1] for arg in arguments])

    create_function = f"{to_name}({full_sig})"
    from_function = f"{from_name}({name_sig})"

    is_table_function = "TABLE" in returns

    query = "SELECT * FROM LATERAL" if is_table_function else "SELECT"

    session.sql(f"""
        CREATE FUNCTION {create_function}
            RETURNS {returns}
            LANGUAGE SQL 
            COMMENT = 'Titan symlink {from_function}'
        AS
        '{query} {from_function}'
    """).collect()
    session.call('titan_state_append', 'links', [f'{from_name}({type_sig})', f'{to_name}({type_sig})'])
    return {"success": True, "message": f"Added link {from_function} -> {create_function}"}

$$
;

CREATE PROCEDURE titan_unlink(target VARCHAR)
    RETURNS OBJECT
    LANGUAGE PYTHON
    RUNTIME_VERSION = '3.8'
    HANDLER = 'unlink'
    PACKAGES = ('snowflake-snowpark-python')
    EXECUTE AS OWNER
AS
$$

import json

def unlink(session, target):
    titan_schema = session.sql("SELECT current_schema()").collect()[0][0];
    if not titan_schema:
        return {"success": False, "exception": "Missing current schema"}

    links = json.loads(session.sql("SELECT titan_state():links").collect()[0][0])
    removed = 0
    for link_from, link_to in links:
        if link_from == target:
            session.sql(f"DROP FUNCTION {link_to}").collect()
            session.call('titan_state_remove', 'links', [link_from, link_to])
            removed += 1
    return {"success": True, "message": f"Removed {removed} links"}

$$
;