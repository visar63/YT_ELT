from airflow import DAG
from datawarehouse.dwh import staging_table, core_table
from dataquality.soda import run_soda_checks
import pendulum
from datetime import timedelta, datetime
from api.video_stats import get_channel_playlist_id, get_video_Ids, get_video_details, save_to_json

from airflow.operators.trigger_dagrun import TriggerDagRunOperator

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


# DAG 1: Define the DAG
with DAG(
    'youtube_video_stats',
    default_args=default_args,
    description='A DAG to fetch YouTube video statistics and save them to a JSON file.',
    schedule='0 14 * * *',  # Run daily at noon
    catchup=False,
) as dag_produce:

    # Define the tasks in the DAG
    playlist_id = get_channel_playlist_id()
    video_ids = get_video_Ids(playlist_id)
    video_details = get_video_details(video_ids)
    save_to_json_task = save_to_json(video_details)

    trigger_update_db = TriggerDagRunOperator(
        task_id='trigger_update_db',
        trigger_dag_id='update_db',  # The DAG ID to trigger
        # wait_for_completion=True,  # Wait for the triggered DAG to complete
        # poke_interval=60,  # Check every 60 seconds
        # reset_dag_run=True,  # Reset the state of the triggered DAG run if it already exists
    )

    # Define dependencies between tasks
    playlist_id >> video_ids >> video_details >> save_to_json_task >> trigger_update_db #type: ignore


# DAG 2: Define the DAG
with DAG(
    'update_db',
    default_args=default_args,
    description='DAG to update the database with YouTube video statistics from the JSON file.',
    schedule=None,  # This DAG will be triggered by the first DAG
    catchup=False,
) as dag_update:

    # Define the tasks in the DAG
    update_staging = staging_table()
    update_core = core_table()

    trigger_data_quality_checks = TriggerDagRunOperator(
        task_id='trigger_data_quality_checks',
        trigger_dag_id='data_quality_checks',  # The DAG ID to trigger
        # wait_for_completion=True,  # Wait for the triggered DAG to complete
        # poke_interval=60,  # Check every 60 seconds
        # reset_dag_run=True,  # Reset the state of the triggered DAG run if it already exists
    )

    # Define dependencies between tasks
    update_staging >> update_core >> trigger_data_quality_checks #type: ignore


# DAG 3: Define the DAG
with DAG(
    'data_quality_checks',
    default_args=default_args,
    description='DAG to run data quality checks using Soda.',
    schedule=None,  # This DAG will be triggered by the first DAG
    catchup=False,
) as dag_data_quality:

    # Define the tasks in the DAG
    soda_validate_staging = run_soda_checks('staging')
    soda_validate_core = run_soda_checks('core')

    # Define dependencies between tasks
    soda_validate_staging >> soda_validate_core #type: ignore
