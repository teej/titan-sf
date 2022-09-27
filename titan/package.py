import os
import json

import sqlglot

TITAN_PATH = os.environ["TITAN_PATH"]


def get_from_ref(package_ref):
    # if left(package_ref, 3) == "git":
    # return get_from_git(package_ref)
    # else:
    return get_from_local(package_ref)


def get_from_local(package_name):
    package_path = os.path.join(TITAN_PATH, package_name)
    if not os.path.exists(package_path):
        raise Exception
    print("ok")
    package_config = {}
    code_files = []
    for filename in os.listdir(package_path):
        if filename.endswith("sql"):
            if filename == f"{package_name}.sql":
                package_config = json.loads(open(os.path.join(package_path, filename), "r").read())
            else:
                code_files.append(filename)
    print("*", package_config)
    for code_file in code_files:
        print(code_file)
        sqlglot.parse(open(os.path.join(package_path, code_file)).read(), read="snowflake")


def get_from_git(git_url):
    pass
