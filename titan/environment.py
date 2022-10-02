"""
    Titan environment within snowflake
"""

import json

from titan import __version__, connect, management


class Environment:
    def __init__(self, db, schema, titan_version, packages):
        self._db = db
        self._schema = schema
        self._titan_version = titan_version
        self._packages = packages

    def __str__(self):
        return f"Environment<{self._db}.{self._schema}, version={self._titan_version}>"

    @property
    def db(self):
        return self._db

    @property
    def schema(self):
        return self._schema

    def has_dependencies(self, deps):
        with connect.env_cursor(self) as cur:
            packs = cur.titan_list()
            for name, version in deps.items():
                if name not in packs:
                    return False
                    # raise Exception(f"Missing dependency {name}")
            # print(deps)
            # return cur.titan_upstate("packages", connect.Sql(f"ARRAY_APPEND(TITAN_STATE():packages, '{pack.id}')"))
        return True


def create(db, schema):
    with connect.scoped_cursor(db) as cur:
        cur.exec(f"CREATE SCHEMA IF NOT EXISTS {db}.{schema}")
        for cmd in management.COMMANDS:
            cur.exec(cmd)
        cur.titan_upstate("titan_version", connect.Sql(f"'{__version__}'::VARIANT"))
        cur.titan_upstate("packages", [])


@connect.using_scoped_cursor
def get(db, schema, cur):
    current_state = cur.titan_state()
    env = Environment(db, schema, **current_state)
    return env


def exists(db, schema):
    with connect.scoped_cursor(db) as cur:
        schemas = cur.fetch(f"SHOW SCHEMAS LIKE '{schema}' IN DATABASE {db}")
        return len(schemas) > 0


@connect.using_scoped_cursor
def destroy(db, schema, cur):
    cur.exec(f"DROP SCHEMA IF EXISTS {db}.{schema} CASCADE")
