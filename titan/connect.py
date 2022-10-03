import contextlib
import json
import os
import typing

from functools import lru_cache as cache
from io import StringIO

import forge
import snowflake.connector
import snowflake.connector.errors

from snowflake.connector.connection import split_statements


@cache
def _conection():
    return snowflake.connector.connect(
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    )


class Sql(typing.NamedTuple):
    code: str

    def __repr__(self) -> str:
        return self.code


class Cursor:
    """
    TODO: Somehow ensure that commands being executed DONT change db/schema
    """

    def __init__(self, cur, db, schema=None):
        self._cur = cur
        self._db = db
        self._schema = schema

    @classmethod
    def add(cls, name, sql, arglist, serde=None):
        @forge.sign(forge.self, *[forge.arg(a) for a in arglist])
        def _func(self, **kwargs):
            params = kwargs.values()
            sql_ = sql.format(*params)
            result = self.fetchone(sql_)[0]
            if serde == "json":
                return json.loads(result)
            elif serde == "bool" and not result:
                raise Exception
            return result

        _func.__name__ = name.lower()
        setattr(cls, _func.__name__, _func)

    @property
    def db(self):
        return self._db

    @property
    def schema(self):
        return self._schema

    def exec(self, query, fetch=False):
        try:
            for stmt, _ in split_statements(StringIO(query), remove_comments=True):
                if stmt:
                    self._cur.execute(stmt)
            if fetch:
                return self._cur.fetchall()
        except snowflake.connector.errors.ProgrammingError:
            raise Exception(f"Error running query [{query}]")

    def fetch(self, query):
        return self.exec(query, fetch=True)

    def fetchone(self, query):
        return self.fetch(query)[0]


@contextlib.contextmanager
def scoped_cursor(db, schema=None):
    with _conection().cursor() as cur:
        cur.execute(f"USE DATABASE {db}")
        if schema:
            cur.execute(f"USE SCHEMA {schema}")
        cur.fetchall()
        yield Cursor(cur, db, schema)


@contextlib.contextmanager
def env_cursor(env):
    with scoped_cursor(env.db, env.schema) as cur:
        yield cur


def using_scoped_cursor(func):
    def wrapper(db, schema, *args, **kwargs):
        with scoped_cursor(db, schema) as cur:
            return func(db, schema, *args, **kwargs, cur=cur)

    return wrapper
