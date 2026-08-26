import logging

logger = logging.getLogger(__name__)  # Set up a logger for this module
logger.setLevel(logging.INFO)

table = "yt_api"  # Define the table name for storing video statistics

def insert_rows(cur, conn, schema, row):
    """
    Inserts a row of data into the specified schema and table in the PostgreSQL database.

    Args:
        cur (psycopg2.extensions.cursor): The database cursor.
        conn (psycopg2.extensions.connection): The database connection.
        schema (str): The name of the schema where the table is located.
        row (dict): A dictionary representing a row of data to be inserted.
    """
    try:
        if schema is None:
            raise ValueError("Schema name must be provided.")
        elif not isinstance(schema, str):
            raise TypeError("Schema name must be a string.")
        
        elif schema == "staging":
            video_id = 'video_id'  # Define the column name for video ID

            # Prepare the SQL query for inserting data into the specified schema and table
            insert_query = f"""
            INSERT INTO {schema}.{table} ("Video_ID", "Video_Title", "Upload_Date", "Duration", "Video_Views", "Likes_Count", "Comment_Count")
            VALUES (%(video_id)s, %(title)s, %(publishedAt)s, %(duration)s, %(viewCount)s, %(likeCount)s, %(commentCount)s)
            """

            cur.execute(insert_query, row)  # Execute the SQL query with the provided row data

        else:
            video_id = 'Video_ID'  # Define the column name for video ID

            # Prepare the SQL query for inserting data into the specified schema and table
            insert_query = f"""
            INSERT INTO {schema}.{table} ("Video_ID", "Video_Title", "Upload_Date", "Duration", "Video_Type", "Video_Views", "Likes_Count", "Comment_Count")
            VALUES (%(Video_ID)s, %(Video_Title)s, %(Upload_Date)s, %(Duration)s, %(Video_Type)s, %(Video_Views)s, %(Likes_Count)s, %(Comment_Count)s)
            """

            cur.execute(insert_query, row)  # Execute the SQL query with the provided row data

        conn.commit()  # Commit the transaction to save changes to the database
        logger.info(f"Row inserted into {schema}.{table}: {row}")  # Log the successful insertion of the row

    except Exception as e:
        logger.error(f"Error inserting row into {schema}.{table}: {e}")  # Log any errors that occur during insertion
        raise

def update_rows(cur, conn, schema, row):
    """
    Updates a row of data in the specified schema and table in the PostgreSQL database.

    Args:
        cur (psycopg2.extensions.cursor): The database cursor.
        conn (psycopg2.extensions.connection): The database connection.
        schema (str): The name of the schema where the table is located.
        row (dict): A dictionary representing a row of data to be updated.
    """
    try:
        if schema is None:
            raise ValueError("Schema name must be provided.")
        elif not isinstance(schema, str):
            raise TypeError("Schema name must be a string.")

        elif schema == "staging":
            update_query = f"""
            UPDATE {schema}.{table}
            SET "Video_Title" = %(title)s,
                "Upload_Date" = %(publishedAt)s,
                "Duration" = %(duration)s,
                "Video_Views" = %(viewCount)s,
                "Likes_Count" = %(likeCount)s,
                "Comment_Count" = %(commentCount)s
            WHERE "Video_ID" = %(video_id)s;
            """

            cur.execute(update_query, row)  # Execute the SQL query with the provided row data

        else:
            # Prepare the SQL query for updating data in the specified schema and table
            update_query = f"""
            UPDATE {schema}.{table}
            SET "Video_Title" = %(Video_Title)s,
                "Upload_Date" = %(Upload_Date)s,
                "Duration" = %(Duration)s,
                "Video_Type" = %(Video_Type)s,
                "Video_Views" = %(Video_Views)s,
                "Likes_Count" = %(Likes_Count)s,
                "Comment_Count" = %(Comment_Count)s
            WHERE "Video_ID" = %(Video_ID)s;
            """

            cur.execute(update_query, row)  # Execute the SQL query with the provided row data

        conn.commit()  # Commit the transaction to save changes to the database
        logger.info(f"Row updated in {schema}.{table}: {row}")  # Log the successful update of the row

    except Exception as e:
        logger.error(f"Error updating row in {schema}.{table}: {e}")  # Log any errors that occur during update
        raise


def delete_rows(cur, conn, schema, ids_to_delete):
    """
    Deletes rows from the specified schema and table in the PostgreSQL database.

    Args:
        cur (psycopg2.extensions.cursor): The database cursor.
        conn (psycopg2.extensions.connection): The database connection.
        schema (str): The name of the schema where the table is located.
        ids_to_delete (list): A list of video IDs to be deleted.
    """
    try:

        if isinstance(ids_to_delete, str):
            ids_to_delete = [ids_to_delete]
        else:
            ids_to_delete = list(ids_to_delete)

        if schema is None:
            raise ValueError("Schema name must be provided.")
        elif not isinstance(schema, str):
            raise TypeError("Schema name must be a string.")

        # Prepare the SQL query for deleting data in the specified schema and table
        delete_query = f"""
        DELETE FROM {schema}.{table}
        WHERE "Video_ID" = ANY(%s);
        """

        cur.execute(delete_query, (ids_to_delete,))  # Execute the SQL query with the provided list of IDs
        conn.commit()  # Commit the transaction to save changes to the database
        logger.info(f"Rows deleted from {schema}.{table}: {ids_to_delete}")  # Log the successful deletion of rows

    except Exception as e:
        logger.error(f"Error deleting rows from {schema}.{table}: {e}")  # Log any errors that occur during deletion
        raise
