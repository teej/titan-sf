import os
import sqlglot

from titan import ast
from titan.connect import Cursor
from titan.management.command import Command


COMMANDS = {}
COMMANDS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "commands")


def _load_commands():
    for filename in os.listdir(COMMANDS_PATH):
        if filename.endswith(".sql"):
            name = filename[:-4].upper()
            source = open(os.path.join(COMMANDS_PATH, filename)).read()
            cmd = Command(name, source)
            COMMANDS[cmd.name] = cmd
            print(filename)
            parsed = sqlglot.parse_one(source, read="snowflake")
            print(repr(parsed))
            name = parsed.this.this.this
            arglist = [ast.arg_name(arg) for arg in ast.get_args(parsed)]

            # return_exp = parsed.find(sqlglot.exp.ReturnsProperty)
            # serde = None
            # # breakpoint()
            # if return_exp and return_exp.args.get("value").this == sqlglot.exp.DataType.Type.OBJECT:
            #     serde = "json"
            serde = ast.serde_for_return_type(parsed)

            trigger = "SELECT" if parsed.find(sqlglot.exp.UserDefinedFunction) else "CALL"

            sql = f"{trigger} {name}(" + (",".join(["{!r}" for _ in arglist])) + ")"
            print(sql)

            Cursor.add(name, sql, arglist, serde)


_load_commands()
