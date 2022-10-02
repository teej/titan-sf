import os
import json

import semver

from sqlglot import exp, parse

from titan import RESERVED_FUNCTION_NAMES, TITAN_PATH, ast

# from constraint import Problem


class Package:
    @classmethod
    def from_local(cls, package_name, package_path):
        try:
            package_config = json.loads(open(os.path.join(package_path, "package.json"), "r").read())
        except Exception as e:
            print("Could not load package config")
            raise e

        code = {}

        for filename in os.listdir(package_path):
            print("->", filename)
            if not filename.endswith(".sql"):
                continue
            code[filename] = open(os.path.join(package_path, filename)).read()

        return cls(package_name, package_config, code)

    def __init__(self, name, config, code):
        try:
            self._name = config["package_name"]
            self._version = semver.VersionInfo.parse(config["version"])
            self._dependencies = config.get("dependencies")
            self._code = code
            self._entities = {}
            self._entity_names = set()
            self._imports = {}
        except KeyError as err:
            raise Exception(f"Package config for [{name}] invalid, missing [{err.args[0]}]")
        if name != self._name:
            raise Exception(f"Package name doesnt match config [{name} != {self._name}]")
        self._unpack()
        self._verify_contents()

    def _unpack(self):
        # For each file, process imports
        # parse
        # use ast to look for identifiers: function calls, tables, etc
        # hard fail if specifying a database/schema IFF it hasn't been imported OR isnt THIS

        for fn, file in self._code.items():
            statements = parse(file, read="snowflake")
            for stmt in statements:
                if ast.is_command(stmt):
                    name, args = ast.parse_command(stmt)
                    if name == "TITAN_IMPORT":
                        for package_ref in args[0]:
                            self._imports[package_ref] = True
                elif stmt:
                    name = ast.func_name(stmt)
                    sig = ast.func_signature(stmt)
                    refs = ast.collect_refs(stmt)
                    prefs = [PackageReference.from_expression(ref) for ref in refs]
                    self._entity_names.add(name.upper())
                    self._entities[sig] = PackageEntity(name=name, sig=sig, statement=stmt, refs=prefs)
        print("done unpacking")
        print(self._entities)

    def _verify_contents(self):
        # Verify references
        for name, entity in self._entities.items():
            print("Verify", entity.sig)
            if name in RESERVED_FUNCTION_NAMES:
                raise Exception(f"Package function {name} is reserved")

            print(entity.refs)
            for ref in entity.refs:
                print("  - entity:", ref)
                if ref.exp_type == exp.Table:
                    raise Exception(f"Package includes a table reference [{ref.full_name()}]")
                elif ref.exp_type == exp.Anonymous:
                    if ref.name in RESERVED_FUNCTION_NAMES:
                        continue
                    elif ref.name.upper() in self._entity_names:
                        continue
                    elif ref.db:
                        raise Exception(f"Cannot specify db [{ref.full_name()}]")
                    elif ref.schema:
                        if ref.schema not in self._imports:
                            raise Exception(f"Cannot specify schema [{ref.full_name()}]")
                    else:
                        raise Exception(f"Dangling reference [{ref.full_name()}]")

    @property
    def dependencies(self):
        return self._dependencies

    @property
    def entities(self):
        return self._entities

    @property
    def imports(self):
        return self._imports

    @property
    def id(self):
        version = str(self._version).replace(".", "_")
        return f"{self._name}__{version}"

    @property
    def name(self):
        return self._name

    def pointer(self):
        return (self._name, self._version)

    def __str__(self):
        return f"Package<{self._name}, {self._version}>"


class PackageEntity:
    def __init__(self, name, sig, statement, refs):
        self.name = name
        self.sig = sig
        self.statement = statement
        self.refs = refs


class PackageReference:
    @classmethod
    def from_expression(cls, ex):
        print(repr(ex))
        if isinstance(ex, exp.UserDefinedFunction):
            args = ast.get_args(ex)
            args = ", ".join([arg.sql() for arg in args])
            return cls(db=None, schema=None, name=ex.name, exp_type=exp.UserDefinedFunction, args=args)
        elif isinstance(ex, exp.Table):
            db = ex.args.get("catalog")
            if db:
                db = db.name
            schema = ex.args.get("db")
            if schema:
                schema = schema.name
            return cls(db=db, schema=schema, name=ex.name, exp_type=exp.Table)
        elif isinstance(ex, exp.Anonymous):
            args = ", ".join(["_"] * ex.expressions)
            return cls(db=None, schema=None, name=ex.name, exp_type=exp.Anonymous, args=args)
        elif isinstance(ex, exp.Dot):
            db, schema = None, None
            while isinstance(ex, exp.Dot):
                if schema:
                    db = schema
                schema = ex.this.name
                ex = ex.expression
            return cls(db=db, schema=schema, name=ex.name, exp_type=type(ex))
        else:
            breakpoint()

    def __init__(self, db, schema, name, exp_type, args=None):
        self.db = db
        self.schema = schema
        self.name = name
        self.exp_type = exp_type
        self.args = args

    def __str__(self):
        return f"PackageRef<{self.full_name()}>"

    def full_name(self):
        db = self.db + "." if self.db else ""
        schema = self.schema + "." if self.schema else ""
        args = f"({self.args})" if self.args else ""
        return f"{db}{schema}{self.name}{args}"


# def get_from_git(git_url):
#     pass


def resolve_dependencies(root):
    dependencies = []
    pointers = {}

    def add(pack):
        name, ver = pack.pointer()
        if name in pointers and ver in pointers[name]:
            return
        if name not in pointers:
            pointers[name] = set()
        pointers[name].add(ver)
        dependencies.extend(pack.dependencies)

    add(root)
    while dependencies:
        dep = dependencies.pop()
        if isinstance(dep, list):
            package_ref, package_version = dep
        elif isinstance(dep, str):
            package_ref, package_version = dep, None
        else:
            raise Exception(f"Unknown dependency {dep}")
        pack = find(package_ref)
        add(pack)
    # print("%" * 120)
    # print(pointers)
    return pointers


def parse_package_ref(package_ref):
    for sep in ["==", ">=", "<=", "~="]:
        if sep in package_ref:
            return package_ref.split(sep)
    return (
        package_ref,
        None,
    )


def find(package_ref):
    # if left(package_ref, 3) == "git":
    # return get_from_git(package_ref)
    # else:
    package_name, version = parse_package_ref(package_ref)

    package_path = os.path.join(TITAN_PATH, package_name)
    if not os.path.exists(package_path):
        raise Exception(f"cannot find package at [{package_path}]")
    return Package.from_local(package_name, package_path)
