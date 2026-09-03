import requests
import pytest
import psycopg2

def test_youtube_api_response(airflow_variable):
    api_key = airflow_variable("api_key")
    channel_handle = airflow_variable("channel_handle")

    url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={channel_handle}&key={api_key}"
    # print(f"Making request to URL: {url}")

    try:
        response = requests.get(url, timeout=30)
        assert response.status_code == 200, f"Expected status code 200, but got {response.status_code}"
    except requests.RequestException as e:
        pytest.fail(f"Error occurred while making the API request: {e}")

def test_real_postgres_connection(real_postgres_connection):
    cursor = None

    try:
        cursor = real_postgres_connection.cursor()
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        assert result[0] == 1, f"Expected result 1, but got {result[0]}"
    except psycopg2.Error as e:
        pytest.fail(f"Error occurred while executing query on PostgreSQL database: {e}")
    finally:
        if cursor:
            cursor.close()
