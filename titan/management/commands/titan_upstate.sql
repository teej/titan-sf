CREATE PROCEDURE TITAN_UPSTATE(key VARCHAR, value VARIANT)
    RETURNS BOOLEAN
    LANGUAGE SQL
    EXECUTE AS CALLER
AS
$$
DECLARE
    new_state VARIANT;
    state_sql VARCHAR;
BEGIN
    new_state := OBJECT_INSERT(TITAN_STATE(), :key, :value, TRUE);
    state_sql := 'SELECT TO_OBJECT(PARSE_JSON(\'' || TO_JSON(:new_state) || '\'))';
    EXECUTE IMMEDIATE
        'CREATE OR REPLACE FUNCTION TITAN_STATE()
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