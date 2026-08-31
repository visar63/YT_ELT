import logging
from venv import logger

#import BashOperator from airflow
from airflow.operators.bash import BashOperator

logger = logging.getLogger(__name__)

SODA_PATH = "/opt/airflow/include/soda"
DATASOURCE = "pg_datasource"


def run_soda_checks(schema):
    """
    This function runs the Soda checks using the BashOperator in Airflow.
    It executes the 'soda scan' command with the specified configuration and checks files.
    """
    soda_command = f"soda scan -d {DATASOURCE} -c {SODA_PATH}/configuration.yml -v SCHEMA={schema} {SODA_PATH}/checks.yml"

    try:
        logger.info(f"Running Soda checks for schema: {schema}")
        logger.info(f"Executing command: {soda_command}")
        # Create a BashOperator to run the Soda checks
        task = BashOperator(
            task_id=f'soda_test_{schema}',
            bash_command=soda_command,
            dag=None  # You can specify your DAG here if needed
        )
        
        return task
    except Exception as e:
        logger.error(f"Error running Soda checks for schema {schema}: {e}")
        raise