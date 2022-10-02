from contextlib import suppress

from sqlglot import exp, parse_one
from sqlglot.optimizer.scope import Scope, traverse_scope


def add_if_not_exists(node):
    if isinstance(node, exp.Create):
        node.set("exists", True)
        return node
    return node


def arg_name(node):
    if not isinstance(node, exp.UserDefinedFunctionKwarg):
        return None
    return node.this.this


def change_name(node, new_name):
    if isinstance(node, exp.UserDefinedFunction):
        node.this.set("this", new_name)
    return node


def func_name(node):
    func = node.find(exp.UserDefinedFunction)
    if func:
        return func.this.sql()


def func_signature(node):
    name = func_name(node)
    args = get_args(node)
    arg_pairs = ", ".join([arg.sql() for arg in args])
    return f"{name}({arg_pairs})"


def get_args(node):
    return node.find_all(exp.UserDefinedFunctionKwarg)


def get_func_ref(node):
    while isinstance(node.parent, (exp.Var, exp.Dot)):
        node = node.parent

    if isinstance(node, (exp.Anonymous, exp.Dot)):
        return node

    raise Exception("bad func")


def collect_refs(node):
    # Create UDF refs
    refs = []
    udf = node.find(exp.UserDefinedFunction)
    if udf:
        # Collect
        with suppress(Exception):
            refs.extend(collect_refs(parse_one(udf.parent.expression.name)))

    else:
        # Collect function references
        for func in node.find_all(exp.Anonymous):
            func = get_func_ref(func).copy()
            func = strip_anon_func(func)
            refs.append(func)
        # Collect table references
        for scope in traverse_scope(node):
            for _, selected_source in scope.selected_sources.values():
                if isinstance(selected_source, exp.Table):
                    refs.append(selected_source)

    # print(repr(node))
    # print("&" * 120)
    # for ref in refs:
    #     print("---->", repr(ref))
    return refs


def get_returns(node):
    return node.find(exp.ReturnsProperty)


def get_return_type(node):
    return get_returns(node).args.get("value")


def has_sproc(node):
    return node.args.get("kind") == "PROCEDURE"


def is_command(node):
    return isinstance(node, exp.Command)


def parse_command(node):
    sproc = parse_one(node.expression.this)
    name = sproc.this
    args = []

    for arg in sproc.expressions:
        if isinstance(arg, exp.Array):
            args.append([e.this for e in arg.expressions])
        else:
            args.append(arg)

    return (name, args)


def serde_for_return_type(node):
    return_type = get_return_type(node).this
    if return_type == exp.DataType.Type.OBJECT:
        return "json"
    elif return_type == exp.DataType.Type.BOOLEAN:
        return "bool"


def strip_or_replace(node):
    if isinstance(node, exp.Create):
        node.set("replace", False)
        return node
    return node


def strip_anon_func(node):
    func_params = len(node.expressions)
    node.set("expressions", func_params)

    def _strip(node):
        if isinstance(node, (exp.Anonymous, exp.Dot, exp.Var)):
            return node

    return node.transform(_strip)
