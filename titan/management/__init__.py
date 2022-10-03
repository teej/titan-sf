import os
import sqlglot

from titan import ast
from titan.connect import Cursor


COMMANDS = []
COMMANDS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "commands")


def _commands():
    prioritize = ["titan_reset.sql", "titan_state.sql"]
    files = os.listdir(COMMANDS_PATH)
    files = [f for f in files if f.endswith(".sql")]
    for priority in prioritize:
        if priority in files:
            files.remove(priority)
            files.insert(0, priority)
    return files


def _load_commands():
    for filename in _commands():
        source = open(os.path.join(COMMANDS_PATH, filename)).read()
        COMMANDS.append(source)
        try:
            parsed = sqlglot.parse(source, read="snowflake")
        except Exception:
            continue
        for statement in parsed:
            if not statement:
                continue
            name = statement.this.this.this
            arglist = [ast.arg_name(arg) for arg in ast.get_args(statement)]
            serde = ast.serde_for_return_type(statement)
            trigger = "CALL" if ast.has_sproc(statement) else "SELECT"
            sql = f"{trigger} {name}(" + (",".join(["{!r}" for _ in arglist])) + ")"

            Cursor.add(name, sql, arglist, serde)


_load_commands()
