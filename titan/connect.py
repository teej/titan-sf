import os


def _con():
    import snowflake.connector

    return snowflake.connector.connect(
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        role=os.environ["SNOWFLAKE_ROLE"],
    )


def execute(query):
    with _con() as con:
        with con.cursor() as cur:
            return cur.execute(query).fetchall()
