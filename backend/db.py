import psycopg2
from quotes import db_quotes

# name of the table to create
TABLE_NAME = "quotes"


def check_if_table_exists(db_conn: dict) -> bool:
    """check if the table already exists"""
    print("Checking if the table exists in the database ...", flush=True)
    check_table_exists_sql = f"""
    SELECT EXISTS (
        SELECT FROM pg_tables
        WHERE schemaname = 'public' AND tablename  = '{TABLE_NAME}'
    )
    """
    # we assume that the table exists
    exists = True
    res = None

    try:
        with psycopg2.connect(
            host=db_conn["host"], user=db_conn["user"], password=db_conn["password"], database=db_conn["name"]
        ) as connection:
            with connection.cursor() as cursor:
                print("Checking if table exists ...", flush=True)
                cursor.execute(check_table_exists_sql)
                res = cursor.fetchone()
            connection.commit()
        exists = res[0]
    except psycopg2.DatabaseError as err:
        print(f"ERROR: check if table exists: {err}", flush=True)
        return False

    print(f"Table exists: {exists}", flush=True)

    # if it exists return ture, otherwise create the table
    # and return true if table creation succeeds
    if exists:
        return True
    created = create_table(db_conn)
    return created


def create_table(db_conn: dict) -> bool:
    """create the table for storing quotes"""

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id SERIAL PRIMARY KEY,
        quote VARCHAR(1000) NOT NULL
    );
    """
    try:
        print("Creating table ...", flush=True)
        with psycopg2.connect(
            host=db_conn["host"], user=db_conn["user"], password=db_conn["password"], database=db_conn["name"]
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(create_table_sql)
            connection.commit()
            insert_default_quotes(db_conn)
            return True
    except psycopg2.DatabaseError as err:
        print(f"ERROR: when creating table: {err}", flush=True)
        return False


def check_connection(db_conn: dict) -> bool:
    """check if the db is connected"""
    print("Attempting to connect to the database ...", flush=True)
    try:
        # try to creat a connection to the database
        with psycopg2.connect(
            host=db_conn["host"], user=db_conn["user"], password=db_conn["password"], database=db_conn["name"]
        ):
            # do nothing, we only want to check if we can connect
            print("Successfully connected to the database.", flush=True)
        return True
    except psycopg2.OperationalError as err:
        print(f"Could not connect to to database, reason: {err}", flush=True)
        return False


def insert_quote(quote: str, db_conn: dict) -> bool:
    """insert a new quote into the database"""
    insert_sql = f"INSERT INTO {TABLE_NAME} (quote) VALUES (%s);"
    try:
        if check_if_table_exists(db_conn):
            with psycopg2.connect(
                host=db_conn["host"], user=db_conn["user"], password=db_conn["password"], database=db_conn["name"]
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(insert_sql, (quote,))
                connection.commit()
                return True
        print("ERROR: table does not exist.")
        return False
    except psycopg2.OperationalError as err:
        print(f"Could not connect to to database, reason: {err}", flush=True)
        return False


def get_quotes(db_conn: dict) -> list:
    """get list of all quotes from the database"""
    select_sql = f"SELECT quote FROM {TABLE_NAME}"
    try:
        if check_if_table_exists(db_conn):
            with psycopg2.connect(
                host=db_conn["host"], user=db_conn["user"], password=db_conn["password"], database=db_conn["name"]
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(select_sql)
                    res = list(cursor.fetchall())
                    if res:
                        quotes = []
                        for row in res:
                            quotes.append(row[0])
                        return quotes
                    return []
        print("ERROR: table does not exist.", flush=True)
        return []
    except psycopg2.DatabaseError as err:
        print(f"ERROR: when getting quotes from the db: {err}")
        return None


def insert_default_quotes(db_conn: dict):
    """insert the default quotes into the database"""
    print("Inserting default quotes into database ...", flush=True)
    for quote in db_quotes:
        insert_quote(quote, db_conn)