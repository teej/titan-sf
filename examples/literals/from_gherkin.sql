-- -- import array-tools
-- -- from array-tools import array_from

-- create or replace function from_gherkin(data VARCHAR)
-- returns table (_row OBJECT)
-- language python
-- runtime_version=3.8
-- handler='Gherkin'
-- as $$

-- """
--   https://github.com/clembou/behave-pandas
-- """

-- import ast

-- def literal_eval_or_str(obj):
--   try:
--     return ast.literal_eval(obj)
--   except (ValueError, SyntaxError):
--     return str(obj)

-- TYPE_FUNCS = {
--   'str': str,
--   'any': literal_eval_or_str,
--   'float': float,
--   'int': int,
-- }

-- class Gherkin:
--   def __init__(self):
--     pass
--   def process(self, data):
--     for n, line in enumerate(data.strip().split('\n')):
--       data = {}
--       processed = [t.strip() for t in line.split('|')[1:-1]]
--       if n == 0:
--         header = processed
--       elif n == 1:
--         types = processed
--       if n > 1:
--         values = processed
--         for i, (col, value) in enumerate(zip(header, values)):
--           type_func = TYPE_FUNCS[types[i]]
--           data[col] = type_func(value)
--         yield (data, )
--   def end_partition(self):
--     pass

-- $$;

-- /*
-- create or replace function from_markdown(data VARCHAR)
-- returns table (_row OBJECT)
-- language SQL
-- as $$
-- WITH count_cols AS (
--   SELECT REGEXP_COUNT(SPLIT_PART(LTRIM(DATA, ' \t\n'), '\n', 1), ',') + 1 as col_count
-- )
-- SELECT
--     _row
-- FROM count_cols
-- JOIN LATERAL from_markdown(array_from('any', col_count), DATA)
-- $$;
-- */

-- -- NOTE TO SELF:
-- -- Use this as a way to build a sane dev environment
-- -- create a daemon for snowsql CLI
-- -- Keep connection open and feed commands to it
-- -- On file save, re-run

