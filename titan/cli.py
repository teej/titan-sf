import re

import click

from titan import TITAN_DEFAULT_SCHEMA, TITAN_LOGO, environment, package, installer


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
    """
    titan: a package manager for snowflake
    """
    _echo_header(f"titan: a package manager for snowflake", header="h1")
    click.echo(TITAN_LOGO)


def _echo_header(message, header="h2"):
    CLI_HEADERS = {"h1": "=", "h2": "-"}
    div = CLI_HEADERS[header]
    message = f" {message} "
    click.echo(f"{div*2}{message:{div}<78}")


@greet.command()
@db_option
@schema_option
@hard_reset_option
def init(db, schema, hard_reset):
    """Initializes titan"""
    _echo_header(f"Initializing titan [db={db} schema={schema}]", header="h2")

    if environment.exists(db, schema):
        if hard_reset:
            click.echo("Existing environment found, resetting")
            environment.reset(db, schema)
        else:
            click.echo("Env already exists, exiting")
            return
    click.echo("Creating environment")
    environment.create(db, schema)
    click.echo("titan environment created successfully")


@greet.command()
@click.argument("package_name")
@db_option
@schema_option
def install(package_name, db, schema):
    """Installs PACKAGE_NAME"""
    _echo_header(f"Installing package: [{package_name}]", header="h2")

    # TODO: enforce single-threaded execution
    env = environment.get(db, schema)

    pack = package.find(package_name)
    click.echo(pack)

    deps = package.resolve_dependencies(pack)

    if not env.has_dependencies(deps):
        # raise Exception(f"Environment missing dependency")
        click.echo("Environment missing dependency")

    # TODO: display expected tree of objects to be installed
    # response = input("Would you like to proceed? [Y/n]")
    # if response != 'Y':
    #     return

    installer.install(env, pack, deps)


# @greet.command()
# @click.argument("package")
# # @click.option("-y", default=False, help="Schema to use") # , is_flag=True, show_default=True, default=False,
# def get(package):


@greet.command()
@click.argument("package_name")
@db_option
@schema_option
def uninstall(package_name, db, schema):
    """Removes PACKAGE_NAME"""
    _echo_header(f"Uninstalling package: [{package_name}]", header="h2")
    env = environment.get(db, schema)


# def list(schema=TITAN_DEFAULT_SCHEMA):
#     raise NotImplementedError

# def upgrade(package, schema=TITAN_DEFAULT_SCHEMA):
#     raise NotImplementedError


# @greet.command()
# @db_option
# @schema_option
# def freeze(db, schema):
#     """
#     Takes all deps in a schema and creates a lockfile? Manifest?
#     """
#     _echo_header(f"Freeze [db={db} schema={schema}]", header="h1")

#     raise NotImplementedError
