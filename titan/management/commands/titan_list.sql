CREATE FUNCTION titan_list()
    RETURNS ARRAY
    LANGUAGE SQL
    EXECUTE AS CALLER
AS
$$
SELECT titan_state():packages::ARRAY
$$
;