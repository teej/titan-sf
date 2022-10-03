from titan import ast, connect


def make_safe(code):
    code = code.transform(ast.add_if_not_exists)
    code = code.transform(ast.strip_or_replace)
    # sprocs: always EXECUTE AS CALLER
    return code


def wire_dependencies(code, deps, this_pack):
    for pack_name, pack_versions in deps.items():
        v = list(pack_versions)[0]
        version = str(v).replace(".", "_")
        fqn = f"{pack_name}__{version}"
        if pack_name == this_pack:
            pack_name = "this"
        code = ast.wire_dependencies(code, pack_name, fqn)
    return code


def prefix_name(code, prefix):
    return code.transform(lambda node: ast.prefix_func_name(node, prefix))


def install(env, pack, deps={}):
    with connect.env_cursor(env) as cur:
        # TODO: need to consider rollback on bad install
        cur.titan_state_append("packages", connect.Sql(f"'{pack.id}'::VARIANT"))
        cur.titan_upstate(pack.id, [])
        version_prefix = f"{pack.id}__"
        for name, entity in pack.entities.items():
            code = entity.statement.copy()
            code = make_safe(code)
            code = wire_dependencies(code, deps, pack.name)
            code = prefix_name(code, version_prefix)
            cur.exec(code.sql(dialect="snowflake"))
            installed_name = ast.func_name(code)
            cur.titan_state_append(pack.id, connect.Sql(f"'{version_prefix}{entity.typesig()}'::VARIANT"))
            cur.titan_link(installed_name, entity.name, entity.args, entity.returns)


def uninstall(env, package_name):
    with connect.env_cursor(env) as cur:
        cur.titan_uninstall(package_name)
