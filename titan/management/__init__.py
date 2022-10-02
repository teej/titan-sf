import os
import sqlglot

from titan import ast
from titan.connect import Cursor


COMMANDS = set()
COMMANDS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "commands")


def _load_commands():
    for filename in os.listdir(COMMANDS_PATH):
        if filename.endswith(".sql"):
            name = filename[:-4].upper()
            source = open(os.path.join(COMMANDS_PATH, filename)).read()

            print(filename)
            parsed = sqlglot.parse(source, read="snowflake")
            for statement in parsed:
                if not statement:
                    continue
                COMMANDS.add(str(statement))

                name = statement.this.this.this
                arglist = [ast.arg_name(arg) for arg in ast.get_args(statement)]

                serde = ast.serde_for_return_type(statement)

                trigger = "CALL" if ast.has_sproc(statement) else "SELECT"

                sql = f"{trigger} {name}(" + (",".join(["{!r}" for _ in arglist])) + ")"

                Cursor.add(name, sql, arglist, serde)


_load_commands()
