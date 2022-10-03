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
