import os
import json

import sqlglot
import semver

from titan import TITAN_PATH

# from constraint import Problem


class Package:
    @classmethod
    def from_local(cls, package_name, package_path):
        try:
            package_config = json.loads(open(os.path.join(package_path, "package.json"), "r").read())
        except Exception as e:
            print("Could not load package config")
            raise e

        contents = []

        for filename in os.listdir(package_path):
            print("->", filename)
            if not filename.endswith(".sql"):
                continue
            codes = sqlglot.parse(open(os.path.join(package_path, filename)).read(), read="snowflake")
            for code in codes:
                contents.append(code)

        return cls(package_name, package_config, contents)

    def __init__(self, name, config, contents):
        try:
            self._name = config["package_name"]
            self._version = semver.VersionInfo.parse(config["version"])
            self._dependencies = config.get("dependencies")
            self._contents = contents
        except KeyError as err:
            raise Exception(f"Package config for [{name}] invalid, missing [{err.args[0]}]")
        if name != self._name:
            raise Exception(f"Package name doesnt match config [{name} != {self._name}]")
        # self._load_contents()
        self._verify_contents()

    # def _load_contents(self):
    #     print(f'found {len(code_files)} files')

    def _verify_contents(self):
        # For each file, process imports
        # parse
        # use ast to look for identifiers: function calls, tables, etc
        # hard fail if specifying a database/schema IFF it hasn't been imported OR isnt THIS
        for c in self._contents:
            print("found ->", str(c))

    @property
    def dependencies(self):
        return self._dependencies

    @property
    def contents(self):
        return self._contents

    @property
    def id(self):
        version = str(self._version).replace(".", "_")
        return f"{self._name}__{version}"

    def pointer(self):
        return (self._name, self._version)

    def __str__(self):
        return f"Package<{self._name}, {self._version}>"


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
    print(pointers)
    return pointers


def parse_package_ref(package_ref):
    parts = package_ref.split("==")
    if len(parts) == 1:
        return (parts[0], None)
    return tuple(parts)

    # return name, version


def find(package_ref):
    # if left(package_ref, 3) == "git":
    # return get_from_git(package_ref)
    # else:
    package_name, version = parse_package_ref(package_ref)

    package_path = os.path.join(TITAN_PATH, package_name)
    if not os.path.exists(package_path):
        raise Exception(f"cannot find package at [{package_path}]")
    return Package.from_local(package_name, package_path)
