import os
import pytest
from unittest.mock import patch
from airflow.models import Connection, Variable, DagBag
import psycopg2

@pytest.fixture()
def api_key():
    with patch.dict(os.environ, {"AIRFLOW_VAR_API_KEY": "MOCK_KEY1234"}):
        yield Variable.get("API_KEY", default_var="MOCK_KEY1234")


@pytest.fixture()
def channel_handle():
    with patch.dict(os.environ, {"AIRFLOW_VAR_CHANNEL_HANDLE": "ArianaGrande"}):
        yield Variable.get("CHANNEL_HANDLE")

@pytest.fixture()
def mock_postgress_conn_vars():

    conn = Connection(
        login="mock_user",
        password="mock_password",
        host="mock_host",
        port=1234,
        schema="mock_schema",
    )
    conn_uri = conn.get_uri()

    with patch.dict(os.environ, {"AIRFLOW_CONN_POSTGRES_DB_YT_ELT": conn_uri}):
        yield Connection.get_connection_from_secrets("POSTGRES_DB_YT_ELT")


@pytest.fixture()
def dag_bag():
    dag_bag = DagBag(dag_folder="dags", include_examples=False)
    yield dag_bag


@pytest.fixture()
def airflow_variable():
    def get_airflow_variable(variable_name):
        env_var = f"AIRFLOW_VAR_{variable_name.upper()}"
        return os.getenv(env_var, None)
    return get_airflow_variable


#test real postgres connection
@pytest.fixture()
def real_postgres_connection():
    dbname = os.getenv("ELT_DATABASE_NAME")
    user = os.getenv("ELT_DATABASE_USERNAME")
    password = os.getenv("ELT_DATABASE_PASSWORD")
    host = os.getenv("POSTGRES_CONN_HOST")
    port = os.getenv("POSTGRES_CONN_PORT")

    conn = None

    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        yield conn
    except psycopg2.Error as e:
        pytest.fail(f"Error occurred while connecting to the PostgreSQL database: {e}")
    finally:
        if conn:
            conn.close()