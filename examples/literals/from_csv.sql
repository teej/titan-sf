CALL TITAN_IMPORT(['arraytools']);


CREATE FUNCTION from_csv(types ARRAY, data VARCHAR)
    RETURNS TABLE (_row OBJECT)
    LANGUAGE PYTHON
    RUNTIME_VERSION = '3.8'
    HANDLER = 'CSV'
AS $$
from io import StringIO
import csv
import ast

def literal_eval_or_str(obj):
  try:
    return ast.literal_eval(obj)
  except (ValueError, SyntaxError):
    return str(obj)

TYPE_FUNCS = {
    'str': str,
    'any': literal_eval_or_str,
}

class CSV:
    def __init__(self):
        pass
    def process(self, types, data):
      reader = csv.DictReader(StringIO(data.strip()), delimiter=',')
      for row in reader:
        typed = {}

        for i, (key, value) in enumerate(row.items()):
          type_func = TYPE_FUNCS[types[i]]
          typed[key] = type_func(value)
        yield (typed,)
    def end_partition(self):
      pass

$$;

CREATE FUNCTION from_csv(data VARCHAR)
    RETURNS TABLE (_row OBJECT)
    LANGUAGE SQL
AS $$
WITH count_cols AS (
    SELECT
        REGEXP_COUNT(
            SPLIT_PART(
                LTRIM(DATA, ' \t\n')
                , '\n', 1)
            , ',') + 1
        as col_count
)
SELECT
    _row
FROM count_cols, LATERAL from_csv(arraytools.array_from('any', col_count), DATA)
$$
;