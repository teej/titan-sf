from titan import ast, connect


def make_safe(code):
    code = code.transform(ast.add_if_not_exists)
    code = code.transform(ast.strip_or_replace)
    # sprocs: always EXECUTE AS CALLER
    return code


def link(cur, source, dest, code):
    args = list(ast.get_args(code))
    arg_names = ",".join([arg.this.this for arg in args])
    arg_pairs = ",".join([arg.sql() for arg in args])
    config = ast.get_return_type(code).sql()
    cur.titan_link(f"{source}({arg_names})", f"{dest}({arg_pairs})", config)


def install(env, pack, deps={}):
    print("installing", pack)
    with connect.env_cursor(env) as cur:
        for code in pack.contents:
            code = make_safe(code)
            dest = ast.func_name(code)
            source = f"{pack.id}__{dest}"
            code = code.transform(lambda node: ast.change_name(node, source))
            cur.exec(code.sql())
            link(cur, source, dest, code)
        cur.titan_upstate("packages", connect.Sql(f"ARRAY_APPEND(TITAN_STATE():packages, '{pack.id}')"))
    print("done")
