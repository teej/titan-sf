import re

import click

from titan import TITAN_DEFAULT_SCHEMA, environment, package, installer

# from titan.package import Package, resolve_dependencies


class SnowflakeIdentifier(click.ParamType):
    name = "string"
    SCHEMA_PATTERN = re.compile(r"^([A-Za-z\_][A-Za-z\_0-9]+)$")

    def convert(self, value, param, ctx):
        if self.SCHEMA_PATTERN.match(value):
            return value
        self.fail(f"{value!r} is not a valid identifier", param, ctx)


db_option = click.option(
    "--database",
    "-d",
    "db",
    help=f"Database to use",
    type=SnowflakeIdentifier(),
)


schema_option = click.option(
    "--schema",
    "-s",
    default=TITAN_DEFAULT_SCHEMA,
    show_default=True,
    help=f"Schema to use",
    type=SnowflakeIdentifier(),
)


hard_reset_option = click.option("--hard-reset", is_flag=True, help=f"Hard reset the Titan environment")


@click.group()
def greet():
    # config.init()
    # CLI setup
    pass


def _echo_header(message, header="h2"):
    # ══ Installing Package: [funnels] ════════════════════════════════════════
    # ══ Installing Package: [funnels] ════════════════════════════════════════
    CLI_HEADERS = {"h1": "=", "h2": "-"}
    div = CLI_HEADERS[header]

    # message = 'Hi'
    # fill = ' '
    # align = '<'
    # width = 16
    # f'{message:{fill}{align}{width}}'
    message = f" {message} "

    click.echo(f"{div*2}{message:{div}<78}")


@greet.command()
@db_option
@schema_option
@hard_reset_option
def init(db, schema, hard_reset):
    """Initializes Titan package manager

    DB - the target database to use
    """
    _echo_header(f"Initializing Titan [db={db} schema={schema}]", header="h1")
    # Check permissions of running user?

    # Create schema
    # Create empty manifest in schema
    # UNSURE: Create schema state (function or table or smth) - is this the manifest? is this the lockfile?

    if environment.exists(db, schema):
        if hard_reset:
            environment.destroy(db, schema)
            print("Old env destroyed")
        else:
            return
    print("Env doesnt exist, creating")

    environment.create(db, schema)
    print("Titan environment created successfully")
    # manifest.create(db=db, schema=schema)
    # lock.create(db=db, schema=schema)


@greet.command()
@click.argument("package_name")
@db_option
@schema_option
def install(package_name, db, schema):
    """Install PACKAGE_NAME"""
    _echo_header(f"Installing package: [{package_name}]", header="h1")

    # Enforce single-threaded execution
    print(package_name, db, schema)
    env = environment.get(db, schema)

    # If manifest doesnt exist, fail?
    # Pip doesnt touch manifests, but node does

    # Create lockfile if not exists
    # Parse package, grab package metadata
    # Add package to manifest
    # Sync manifest to lockfile
    # Sync lockfile to dependency code

    pack = package.find(package_name)
    print(pack)
    # if package ref is remote, download

    deps = package.resolve_dependencies(pack)

    # # display expected tree of objects to be installed
    # response = input("Would you like to proceed? [Y/n]")
    # if response != 'Y':
    #     return

    installer.install(env, pack)

    # installer.install(env, package.find("arraytools==1.0.0"))
    # installer.install(env, package.find("datatools"), deps={"arraytools": "arraytools__1_0_0"})

    # raise NotImplementedError


# @greet.command()
# @click.argument("package")
# # @click.option("-y", default=False, help="Schema to use") # , is_flag=True, show_default=True, default=False,
# def get(package):

# def uninstall(package, schema=TITAN_DEFAULT_SCHEMA):
#     raise NotImplementedError


# def list(schema=TITAN_DEFAULT_SCHEMA):
#     raise NotImplementedError

# def upgrade(package, schema=TITAN_DEFAULT_SCHEMA):
#     raise NotImplementedError


@greet.command()
@db_option
@schema_option
def freeze(db, schema):
    """
    Takes all deps in a schema and creates a lockfile? Manifest?
    """
    _echo_header(f"Freeze [db={db} schema={schema}]", header="h1")

    raise NotImplementedError
