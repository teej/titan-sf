CREATE PROCEDURE titan_import(package_names ARRAY)
    RETURNS VARCHAR
    LANGUAGE SQL
    EXECUTE AS CALLER
AS
$$
DECLARE
    q VARCHAR;
BEGIN
    q := (SELECT titan_assert( :PACKAGE_NAMES = array_intersection(titan_state():packages, :PACKAGE_NAMES) ));
END;
$$
;



    -- EXECUTE IMMEDIATE 'SELECT titan_assert(, titan_state():packages)';
    -- titan_path := (SELECT TITAN.THIS.PATH( :PACKAGE_NAMES ));
    -- path := '$current, $public, ' || :titan_path;
    -- EXECUTE IMMEDIATE 'ALTER SESSION SET SEARCH_PATH = \'' || :path || '\'';
    -- RETURN :path;