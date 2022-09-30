CREATE PROCEDURE TITAN_LINK(link_from VARCHAR, link_to VARCHAR, returns VARCHAR)
    RETURNS BOOLEAN
    LANGUAGE SQL
    EXECUTE AS CALLER
AS
$$
BEGIN
    EXECUTE IMMEDIATE
        'CREATE FUNCTION IF NOT EXISTS ' || :link_to ||
        ' RETURNS ' || :returns || 
        ' LANGUAGE SQL ' ||
        ' COMMENT = \$\$Titan symlink to ' || :link_from || '\$\$' ||
        ' AS \$\$ SELECT ' || :link_from || '\$\$';
    RETURN TRUE;

END;
$$