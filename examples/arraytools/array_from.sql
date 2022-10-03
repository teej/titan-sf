CREATE FUNCTION array_from(
  value VARIANT,
  len FLOAT
)
  RETURNS ARRAY
  LANGUAGE JAVASCRIPT
AS $$
return Array.from({length: LEN}, (x, y) => VALUE);
$$
;

-- TODO: implement OVERLOAD
-- CALL TITAN.OVERLOAD('array_from', ['VARCHAR', 'FLOAT']);
-- CALL TITAN.OVERLOAD('array_from', ['NUMERIC', 'FLOAT']);

CREATE FUNCTION array_from(value VARCHAR, len FLOAT)
  RETURNS ARRAY
  LANGUAGE SQL
AS $$
SELECT this.array_from(VALUE::VARIANT, LEN)
$$
;

CREATE FUNCTION array_from(value NUMERIC, len FLOAT)
  RETURNS ARRAY
  LANGUAGE SQL
AS $$
SELECT this.array_from(VALUE::VARIANT, LEN)
$$
;
