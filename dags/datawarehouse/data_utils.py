from airflow.providers.postgres.hooks.postgres import PostgresHook

from psycopg2.extras import RealDictCursor

table_name = "yt_api"  # Define the table name for storing video statistics

def get_conn_cursor() -> tuple:
    """
    Establishes a connection to the PostgreSQL database using Airflow's PostgresHook.

    Returns:
        PostgresHook: An instance of PostgresHook connected to the specified PostgreSQL database.
    """
    # Create a PostgresHook instance with the connection ID defined in Airflow
    hook = PostgresHook(postgres_conn_id='postgres_db_yt_elt', database='elt_db')
    conn = hook.get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    return conn, cur

def close_conn_cursor(conn, cur):
    """
    Closes the cursor and connection to the PostgreSQL database.

    Args:
        conn (psycopg2.extensions.connection): The database connection.
        cur (psycopg2.extensions.cursor): The database cursor.
    """
    cur.close()  # Close the cursor to avoid resource leaks
    conn.close()  # Close the connection to avoid resource leaks


def create_schema(schema_name: str):
    """
    Creates a schema in the PostgreSQL database if it does not already exist.

    Args:
        schema_name (str): The name of the schema to create.
    """
    conn, cur = get_conn_cursor()  # Get a connection and cursor
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name};")  # Execute the SQL command to create the schema
    conn.commit()  # Commit the transaction
    close_conn_cursor(conn, cur)  # Close the connection and cursor


def create_table(schema_name: str, table_name: str):
    """
    Creates a table in the specified schema of the PostgreSQL database if it does not already exist.

    Args:
        schema_name (str): The name of the schema where the table will be created.
        table_name (str): The name of the table to create.
    """
    conn, cur = get_conn_cursor()  # Get a connection and cursor

    if schema_name is None or table_name is None:
        raise ValueError("Schema name and table name must be provided.")

    elif not isinstance(schema_name, str) or not isinstance(table_name, str):
        raise TypeError("Schema name and table name must be strings.")

    elif schema_name == "staging":
        table_sql = f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
                "Video_ID" VARCHAR(12) PRIMARY KEY NOT NULL,
                "Video_Title" TEXT NOT NULL,
                "Upload_Date" TIMESTAMP NOT NULL,
                "Duration" VARCHAR(20) NOT NULL,
                "Video_Views" INT,
                "Likes_Count" INT,
                "Comment_Count" INT
            );
        """ 
    else:
        table_sql = f"""
            CREATE TABLE IF NOT EXISTS {schema_name}.{table_name} (
                "Video_ID" VARCHAR(12) PRIMARY KEY NOT NULL,
                "Video_Title" TEXT NOT NULL,
                "Upload_Date" TIMESTAMP NOT NULL,
                "Duration" TIME NOT NULL,
                "Video_Type" VARCHAR(10) NOT NULL,
                "Video_Views" INT,
                "Likes_Count" INT,
                "Comment_Count" INT
            );
        """

    cur.execute(table_sql)  # Execute the SQL command to create the table
    conn.commit()  # Commit the transaction
    close_conn_cursor(conn, cur)  # Close the connection and cursor


def get_video_ids(cur, schema_name: str, table_name: str) -> list:
    """
    Retrieves all video IDs from the specified table in the PostgreSQL database.

    Args:
        cur (psycopg2.extensions.cursor): The database cursor.
        schema_name (str): The name of the schema where the table is located.
        table_name (str): The name of the table from which to retrieve video IDs.

    Returns:
        list: A list of video IDs retrieved from the specified table.
    """
    if schema_name is None or table_name is None:
        raise ValueError("Schema name and table name must be provided.")

    elif not isinstance(schema_name, str) or not isinstance(table_name, str):
        raise TypeError("Schema name and table name must be strings.")

    query = f"SELECT \"Video_ID\" FROM {schema_name}.{table_name};"
    cur.execute(query)  # Execute the SQL command to retrieve video IDs
    ids = cur.fetchall()  # Fetch all results from the executed query

    video_ids = [row["Video_ID"] for row in ids]  # Extract video IDs from the result set
    return video_ids # that will return: ['VIDEO_ID1', 'VIDEO_ID2', ...]