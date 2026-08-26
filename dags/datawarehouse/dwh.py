from datawarehouse.data_modification import insert_rows, update_rows, delete_rows
from datawarehouse.data_transformation import transform_data
from datawarehouse.data_loading import load_data
from datawarehouse.data_utils import get_conn_cursor, close_conn_cursor, create_schema, create_table, get_video_ids

import logging
from airflow.decorators import task

"""
Data Warehouse Management Module
This module contains functions to manage the staging and core tables in the data warehouse.
"""

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

table = "yt_api"  # Define the table name for storing video statistics

@task
def staging_table():
    schema_name = "staging"  # Define the schema name for staging
    conn, cur = None, None  # Initialize connection and cursor variables

    try:
        conn, cur = get_conn_cursor()  # Get database connection and cursor

        YT_data = load_data(0)  # Load data from the JSON file
        if YT_data is None:
            logger.error("No data loaded. Exiting the staging_table task.")
            return  # Exit the function if no data is loaded

        create_schema(schema_name)  # Create the staging schema if it doesn't exist
        create_table(schema_name, table)  # Create the staging table if it doesn't exist

        table_ids = get_video_ids(cur, schema_name, table)  # Get existing video IDs from the database

        for row in YT_data:
            if len(table_ids) == 0 or row['video_id'] not in table_ids:
                insert_rows(cur, conn, schema_name, row)  # Insert new rows into the staging schema_name
            else:
                update_rows(cur, conn, schema_name, row)  # Update existing rows in the staging table

        ids_in_json = {row['video_id'] for row in YT_data}  # Get video IDs from the loaded JSON data
        ids_to_delete = set(table_ids) - ids_in_json  # Determine which IDs need to be deleted from the database
        for video_id in ids_to_delete:
            delete_rows(cur, conn, schema_name, video_id)  # Delete rows from the staging table that are not in the JSON data

        logger.info("Staging table updated successfully.")  # Log a success message
            


    except Exception as e:
        logger.error(f"Error occurred while creating staging table: {e}")
        raise  # Re-raise the exception to propagate it up the call stack
    finally:
        close_conn_cursor(conn, cur)  # Close the database connection and cursor


@task
def core_table():
    schema_name = "core"  # Define the schema name for the core table
    conn, cur = None, None  # Initialize connection and cursor variables

    try:
        conn, cur = get_conn_cursor()  # Get database connection and cursor

        create_schema(schema_name)  # Create the core schema if it doesn't exist
        create_table(schema_name, table)  # Create the core table if it doesn't exist

        table_ids = get_video_ids(cur, schema_name, table)  # Get existing video IDs from the core table

        current_video_ids = set()  # Initialize a set to keep track of current video IDs

        cur.execute(f"SELECT * FROM staging.{table}")  # Fetch all rows from the staging table
        staging_rows = cur.fetchall()  # Fetch all rows from the staging table

        for row in staging_rows:
            video_id = row["Video_ID"]
            current_video_ids.add(video_id)  # Add the video ID to the current set

            if len(table_ids) == 0 or video_id not in table_ids:
                transformed_row = transform_data(row)  # Transform the data before inserting into the core table
                insert_rows(cur, conn, schema_name, transformed_row)  # Insert new rows into the core table
            else:
                transformed_row = transform_data(row)
                update_rows(cur, conn, schema_name, transformed_row)  # Update existing rows in the core table

        ids_to_delete = set(table_ids) - current_video_ids  # Determine which IDs need to be deleted from the core table
        for video_id in ids_to_delete:
            delete_rows(cur, conn, schema_name, video_id)  # Delete rows from the core table that are not in the current set


        logger.info("Core table updated successfully.")  # Log a success message

    except Exception as e:
        logger.error(f"Error occurred while updating core table: {e}")
        raise  # Re-raise the exception to propagate it up the call stack
    finally:
        close_conn_cursor(conn, cur)  # Close the database connection and cursor
