CREATE PROCEDURE titan_link(link_from VARCHAR, link_to VARCHAR, returns VARCHAR)
    RETURNS OBJECT
    LANGUAGE PYTHON
    RUNTIME_VERSION = '3.8'
    HANDLER = 'link'
    PACKAGES = ('snowflake-snowpark-python')
    EXECUTE AS OWNER
AS
$$

def link(session, link_from, link_to, returns):
    titan_schema = session.sql("SELECT current_schema()").collect()[0][0];
    if not titan_schema:
        return {"success": False, "exception": "Missing current schema"}

    session.sql(f"""
        CREATE FUNCTION {link_to}
            RETURNS {returns}
            LANGUAGE SQL 
            COMMENT = 'Titan symlink {link_from}'
        AS
        'SELECT {link_from}'
    """).collect()
    session.sql(f"""
        CALL titan_upstate(
            'links',
            ARRAY_APPEND(TITAN_STATE():links, ['{link_from}', '{link_to}'])
        )
    """).collect()
    return {"success": True, "message": f"Added link {link_from} -> {link_to}"}

$$
;

CREATE PROCEDURE titan_unlink(target_link_to VARCHAR)
    RETURNS OBJECT
    LANGUAGE PYTHON
    RUNTIME_VERSION = '3.8'
    HANDLER = 'unlink'
    PACKAGES = ('snowflake-snowpark-python')
    EXECUTE AS OWNER
AS
$$

import json

def _sig_types_only(full_sig):
    name, kwargs = full_sig.split("(")
    kwargs = kwargs.split(")")[0].split(",")
    kwargs = [arg.strip().split(' ')[-1] for arg in kwargs]
    kwargs = ','.join(kwargs)

    return f"{name}({kwargs})"

def unlink(session, target_link_to):
    titan_schema = session.sql("SELECT current_schema()").collect()[0][0];
    if not titan_schema:
        return {"success": False, "exception": "Missing current schema"}

    links = json.loads(session.sql("SELECT titan_state():links").collect()[0][0])
    for link_from, link_to in links:
        if link_to == target_link_to:
            sig = _sig_types_only(target_link_to)
            links.remove([link_from, link_to])
            session.sql(f"DROP FUNCTION {sig}").collect()
            session.sql(f"""
                CALL titan_upstate(
                    'links',
                    {json.dumps(links)}
                )
            """).collect()
            return {"success": True, "message": f"Removed link {link_from} -> {link_to}"}

$$
;