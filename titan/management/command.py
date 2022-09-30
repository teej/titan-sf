# from . import COMMANDS_PATH

class Command:
    # @classmethod
    # def from_sql(cls, sql):
    #     cls(source=sql)

    def __init__(self, name, source):
        self._name = name
        self._source = source

    @property
    def name(self):
        return self._name

    @property
    def source(self):
        return self._source
