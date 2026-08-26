from airflow import DAG
from datawarehouse.dwh import staging_table, core_table
import pendulum
from datetime import timedelta, datetime
from api.video_stats import get_channel_playlist_id, get_video_Ids, get_video_details, save_to_json

# Define the local timezone
local_tz = pendulum.timezone("Europe/Belgrade")

# Define default arguments for the DAG
default_args = {
    'owner': 'data_engineers',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'email': ['data_engineers@example.com'],
    # 'retries': 1,
    # 'retry_delay': timedelta(minutes=5),
    'max_active_runs': 1,
    'dagrun_timeout': timedelta(hours=1),
    'start_date': datetime(2026, 7, 31, tzinfo=local_tz),
    # 'end_date': datetime(2024, 12, 31, tzinfo=local_tz),
}


# Define the DAG
with DAG(
    'youtube_video_stats',
    default_args=default_args,
    description='A DAG to fetch YouTube video statistics and save them to a JSON file.',
    schedule='0 12 * * *',  # Run daily at noon
    catchup=False,
) as dag:

    # Define the tasks in the DAG
    playlist_id = get_channel_playlist_id()
    video_ids = get_video_Ids(playlist_id)
    video_details = get_video_details(video_ids)
    save_to_json_task = save_to_json(video_details)

    # Define dependencies between tasks
    playlist_id >> video_ids >> video_details >> save_to_json_task #type: ignore


# Define the DAG
with DAG(
    'update_db',
    default_args=default_args,
    description='DAG to update the database with YouTube video statistics from the JSON file.',
    schedule='0 15 * * *',  # Run daily at noon
    catchup=False,
) as dag:

    # Define the tasks in the DAG
    update_staging = staging_table()
    update_core = core_table()

    # Define dependencies between tasks
    update_staging >> update_core #type: ignore
