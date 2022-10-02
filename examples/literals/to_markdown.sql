-- -- import array-tools
-- -- from array-tools import array_from

-- create or replace function to_markdown(headers ARRAY, _row ARRAY)
-- returns table (_row VARCHAR)
-- language python
-- runtime_version=3.8
-- handler='Markdown'
-- as $$

-- DDL = """
-- create or replace function to_markdown(headers ARRAY, _row ARRAY)
--   returns table (_row VARCHAR)
--   language python
--   runtime_version=3.8
--   handler='Markdown'
-- """

-- class Markdown:
--   def __init__(self):
--     self.records = []
--     self.initialized = False

--   def _to_markdown(self, record, fill=' '):
--     markdown = []
--     for col, item in enumerate(record):
--       width = self.column_widths[col]
--       markdown.append(f"{fill}{str(item).ljust(width, fill)}{fill}")
--     markdown = [''] + markdown + ['']
--     return '|'.join(markdown)

--   def process(self, headers, row):
    
--     if not self.initialized:
--       self.initialized = True
--       self.num_columns = len(row)
--       self.column_widths = [len(str(item)) for item in headers]
--       self.records.append(headers)

--     self.records.append(row)
--     for i, item in enumerate(row):
--       width = len(str(item))
--       if width > self.column_widths[i]:
--         self.column_widths[i] = width
        
--   def end_partition(self):
--     yield (self._to_markdown(self.records[0]), )
--     yield (self._to_markdown(['-']*self.num_columns, fill='-'),)
--     for record in self.records[1:]:
--       yield (self._to_markdown(record), )

-- $$;
