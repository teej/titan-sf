from titan import ast, connect


def make_safe(code):
    code = code.transform(ast.add_if_not_exists)
    code = code.transform(ast.strip_or_replace)
    # sprocs: always EXECUTE AS CALLER
    return code


def wire_dependencies(code, deps, this_pack):
    print(deps)
    for pack_name, pack_versions in deps.items():
        v = list(pack_versions)[0]
        version = str(v).replace(".", "_")
        fqn = f"{pack_name}__{version}"
        if pack_name == this_pack:
            pack_name = "this"
        code = ast.wire_dependencies(code, pack_name, fqn)
    return code


def link(cur, source, dest, code):
    args = list(ast.get_args(code))
    arg_names = ",".join([arg.this.this for arg in args])
    arg_pairs = ",".join([arg.sql() for arg in args])
    config = ast.get_return_type(code).sql()
    from_ = f"{source}({arg_names})"
    to = f"{dest}({arg_pairs})"
    # breakpoint()
    # x = ast.get_return_type(code)
    # Table Function
    if ast.is_table_function(code):
        from_ = " * FROM LATERAL " + from_
    cur.titan_link(from_, to, config)


def install(env, pack, deps={}):
    print("installing", pack)
    with connect.env_cursor(env) as cur:
        # TODO: this needs to happen after package successfully installed
        cur.titan_upstate("packages", connect.Sql(f"ARRAY_APPEND(TITAN_STATE():packages, '{pack.id}')"))
        for name, entity in pack.entities.items():
            code = entity.statement.copy()
            code = make_safe(code)
            code = wire_dependencies(code, deps, pack.name)

            dest = ast.func_name(code)
            source = f"{pack.id}__{dest}"

            code = code.transform(lambda node: ast.change_name(node, source))
            print("~" * 120)
            print(code.sql(dialect="snowflake"))

            cur.exec(code.sql(dialect="snowflake"))
            # cur.titan_upstate("entities", connect.Sql(f"ARRAY_APPEND(TITAN_STATE():packages, '{pack.id}')"))
            # link(cur, source, dest, code)
        # cur.titan_upstate("packages", connect.Sql(f"ARRAY_APPEND(TITAN_STATE():packages, '{pack.id}')"))
    print("done")


def uninstall(env, pack):
    with connect.env_cursor(env) as cur:
        cur.titan_uninstall(pack.id)
