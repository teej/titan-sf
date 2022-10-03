"""
    Titan environment within snowflake
"""

import json

from titan import __version__, connect, management


class Environment:
    def __init__(self, db, schema, titan_version, packages, links):
        self._db = db
        self._schema = schema
        self._titan_version = titan_version
        self._packages = packages
        self._links = links

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
            packs = cur.titan_packages()
            for name, version in deps.items():
                if name not in packs:
                    return False
                    # raise Exception(f"Missing dependency {name}")
        return True


def create(db, schema):
    with connect.scoped_cursor(db, schema) as cur:
        for cmd in management.COMMANDS:
            cur.exec(cmd)
        cur.titan_upstate("titan_version", connect.Sql(f"'{__version__}'::VARIANT"))
        cur.titan_upstate("packages", [])
        cur.titan_upstate("links", [])


@connect.using_scoped_cursor
def get(db, schema, cur):
    state = cur.titan_state()
    env = Environment(db, schema, state["titan_version"], state["packages"], state["links"])
    return env


def exists(db, schema):
    with connect.scoped_cursor(db) as cur:
        schemas = cur.fetch(f"SHOW SCHEMAS LIKE '{schema}' IN DATABASE {db}")
        if not schemas:
            return False
    with connect.scoped_cursor(db, schema) as cur:
        funcs = cur.fetch(f"SHOW FUNCTIONS LIKE 'titan_state' IN SCHEMA {schema}")
        if not funcs:
            return False
        return True
        # TODO: do version checking
        # state = cur.titan_state()
        # return "titan_version" in state


@connect.using_scoped_cursor
def reset(db, schema, cur):
    cur.titan_reset()
