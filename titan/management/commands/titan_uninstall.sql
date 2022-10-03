CREATE OR REPLACE PROCEDURE titan_uninstall(package_ref VARCHAR)
    RETURNS VARIANT
    LANGUAGE PYTHON
    RUNTIME_VERSION = '3.8'
    HANDLER = 'uninstall'
    PACKAGES = ('snowflake-snowpark-python')
    EXECUTE AS OWNER
AS
$$

import json

from snowflake.snowpark.functions import lit, to_variant

def uninstall(session, package):
    titan_schema = session.sql("SELECT current_schema()").collect()[0][0]
    if not titan_schema:
        return {"exception": "Missing current schema"}

    state = json.loads(session.sql("SELECT titan_state()").collect()[0][0])
    to_uninstall = []
    for pack in state["packages"]:
        name, version = pack.split("__")
        if name == package:
            to_uninstall.append(pack)
    for pack in to_uninstall:
        entities = state[pack]
        # Unlink
        for ent in entities:
            session.call('titan_unlink', ent)
        # Drop
        for ent in entities:
            session.sql(f"DROP FUNCTION {ent}").collect()
        session.call('titan_state_del', pack)
        session.call('titan_state_remove', 'packages', to_variant(lit(pack)))

    return {"success": True, "message": f"Successfully removed {package}"}

$$
;