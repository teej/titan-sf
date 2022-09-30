from sqlglot import exp


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
    if isinstance(node, (exp.UserDefinedFunction, exp.StoredProcedure)):
        node.this.set("this", new_name)
    return node

    # func = node.find
    # if func:
    # return sql(func.this)


def func_name(node):
    func = node.find(exp.UserDefinedFunction, exp.StoredProcedure)
    if func:
        return sql(func.this)


def get_args(node):
    return node.find_all(exp.UserDefinedFunctionKwarg)


def get_returns(node):
    return node.find(exp.ReturnsProperty)


def get_return_type(node):
    return get_returns(node).args.get("value")


def serde_for_return_type(node):
    return_type = get_return_type(node).this
    # if return_type:
    #     return_type = returns.args.get("value").this
    if return_type == exp.DataType.Type.OBJECT:
        return "json"
    elif return_type == exp.DataType.Type.BOOLEAN:
        return "bool"


def sql(node):
    return node.sql()  # write="snowflake"


def strip_or_replace(node):
    if isinstance(node, exp.Create):
        node.set("replace", False)
        return node
    return node
