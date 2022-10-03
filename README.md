```
    __  _ __          
   / /_(_) /____ ____ 
  / __/ / __/ _ `/ _ \
  \__/_/\__/\_,_/_//_/
   
```


a package manager for the snowflake data warehouse

## Getting Started

### Installing titan-cli

Use pip to install titan

```sh
python3 -m pip install "git+https://github.com/teej/titan-sf.git"
```

Use `titan init` to create a titan environment within a Snowflake schema (`TITAN` by default). 

```sh
python3 -m titan init -d <database> -s <schema>
```

Point titan to a package directory, and install a package

```sh
export TITAN_PATH='./examples/'
python3 -m titan install <package> -d <database> -s <schema>
```

### Permissions

titan creates and destroys database objects. For that reason it is best practice to use a standalone user & role.

```SQL
USE ROLE USERADMIN;
CREATE ROLE titan_role;
CREATE USER titan
    DEFAULT_ROLE = 'titan_role'
    PASSWORD = '<password>';
GRANT ROLE titan_role TO USER titan;

USE ROLE <dev_role>;
USE DATABASE <dev_db>;
CREATE SCHEMA TITAN;
GRANT OWNERSHIP ON SCHEMA TITAN TO ROLE titan_role;

GRANT USAGE ON DATABASE <dev_db> TO ROLE titan_role;
GRANT USAGE ON SCHEMA TITAN TO ROLE titan_role;
GRANT USAGE ON WAREHOUSE <dev_wh> TO ROLE titan_role;
GRANT CREATE FUNCTION ON SCHEMA TITAN TO ROLE titan_role;
GRANT CREATE PROCEDURE ON SCHEMA TITAN TO ROLE titan_role;
```

### Connecting

titan reads these environment variables to connect to snowflake

```sh
export SNOWFLAKE_USER="<user>"
export SNOWFLAKE_PASSWORD="<pass>"
export SNOWFLAKE_ACCOUNT="<acct>"
export SNOWFLAKE_ROLE="<role>"
export SNOWFLAKE_WAREHOUSE="<wh>"
```

## Known issues

This is, at best, alpha software.

- titan is slow. It relies heavily on python stored procedures which have a high fixed performance overhead.
- Only supports user-defined functions. Stored procedures, tables, and views are coming soon.
- Does not fully support dependency resolution.
- titan does not have a package repository. Currently, only installing from local is supported.
