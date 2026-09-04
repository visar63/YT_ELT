# YT_ELT

YouTube ELT pipeline built with Apache Airflow, Docker, PostgreSQL, and Soda data quality checks.

The project extracts video metadata and statistics from the YouTube Data API, saves the raw response as a dated JSON file, loads it into a PostgreSQL staging table, transforms the records, writes the final data into a core table, and validates both warehouse layers with Soda. The extraction DAG now triggers the database update DAG, which then triggers the data quality DAG.

## Stack

- Apache Airflow 2.9.2
- Python 3.10
- PostgreSQL 13
- Docker Compose
- YouTube Data API v3
- Soda Core for PostgreSQL

## Project Structure

```text
.
|-- dags/
|   |-- main.py                         # Airflow DAG definitions
|   |-- api/
|   |   `-- video_stats.py              # YouTube API extraction tasks
|   |-- dataquality/
|   |   `-- soda.py                     # Soda scan Airflow task factory
|   `-- datawarehouse/
|       |-- data_loading.py             # Loads dated JSON files
|       |-- data_modification.py        # Insert, update, delete helpers
|       |-- data_transformation.py      # Duration parsing and core mapping
|       |-- data_utils.py               # Postgres connection/table helpers
|       `-- dwh.py                      # Staging and core Airflow tasks
|-- data/                               # Extracted JSON files
|-- include/soda/
|   |-- configuration.yml               # Soda PostgreSQL datasource config
|   `-- checks.yml                      # Soda checks for yt_api tables
|-- tests/
|   |-- conftest.py                     # Pytest fixtures for Airflow, API, and Postgres checks
|   |-- integration_test.py             # YouTube API and real Postgres connection tests
|   `-- unit_test.py                    # Variable, connection, and DAG integrity tests
|-- docker/postgres/
|   `-- init-multiple-databases.sh      # Creates Airflow and ELT databases
|-- docker-compose.yaml                 # Local Airflow stack
|-- Dockerfile                          # Custom Airflow image
`-- requirements.txt
```

## Pipeline

The Airflow project defines three DAGs. All DAGs use the `Europe/Belgrade` timezone, start from `2026-07-31`, disable catchup, and allow one active run at a time.

### `youtube_video_stats`

Runs the extraction flow:

1. Gets the channel upload playlist ID.
2. Gets video IDs from the playlist.
3. Fetches video details from the YouTube Data API in batches of up to 50 video IDs.
4. Saves the extracted records to `data/video_details_<YYYY-MM-DD>.json`.
5. Triggers the `update_db` DAG.

Schedule: daily at `14:00` in the configured DAG timezone.

### `update_db`

Runs the database load and transformation flow:

1. Loads the current dated JSON file from `data/`.
2. Creates the `staging` schema/table if needed.
3. Inserts or updates raw YouTube records in `staging.yt_api`.
4. Creates the `core` schema/table if needed.
5. Reads staging rows, transforms them, and inserts or updates `core.yt_api`.
6. Deletes rows that no longer exist in the latest source file.
7. Triggers the `data_quality_checks` DAG.

Schedule: manual or triggered by `youtube_video_stats`.

### `data_quality_checks`

Runs Soda scans against both warehouse schemas:

1. Validates `staging.yt_api`.
2. Validates `core.yt_api`.

Schedule: manual or triggered by `update_db`. The DAG uses the shared Soda files in `include/soda/`.

## Data Snapshots

The `data/` directory contains extracted JSON snapshots named with the extraction date. The latest checked-in snapshot is:

```text
data/video_details_2026-09-03.json
```

The loader reads the file for the current date when `update_db` runs, so trigger `youtube_video_stats` first if today's JSON file does not exist yet.

## Database Tables

### `staging.yt_api`

Stores raw API-shaped data using warehouse column names:

- `Video_ID`
- `Video_Title`
- `Upload_Date`
- `Duration`
- `Video_Views`
- `Likes_Count`
- `Comment_Count`

### `core.yt_api`

Stores transformed data:

- `Video_ID`
- `Video_Title`
- `Upload_Date`
- `Duration`
- `Video_Type`
- `Video_Views`
- `Likes_Count`
- `Comment_Count`

`Video_Type` is derived from duration:

- `Shorts` for videos under 1 minute
- `Normal` for videos 1 minute or longer

## Data Quality Checks

Soda is configured in `include/soda/configuration.yml` and reads the same PostgreSQL environment variables used by the ELT database connection.

Checks are defined in `include/soda/checks.yml` for the `yt_api` table in the selected schema. Current validations include:

- `Video_ID` must not be missing.
- `Video_ID` must not be duplicated.
- `Likes_Count` must not be greater than `Video_Views`.
- `Comment_Count` must not be greater than `Video_Views`.

The Airflow task passes the schema dynamically with `SCHEMA=staging` or `SCHEMA=core`, so the same checks file can validate both layers.

## Tests

The project includes Pytest coverage for configuration, Airflow DAG integrity, the YouTube API connection, and the PostgreSQL connection.

Run tests inside an Airflow container:

```powershell
docker exec -it airflow-scheduler pytest /opt/airflow/tests
```

Or run them locally from the project root after installing dependencies and setting the required environment variables:

```powershell
pytest tests
```

The integration tests require valid YouTube API variables and a reachable PostgreSQL database.

## Environment Variables

Create a `.env` file in the project root. Do not commit real credentials or API keys.

Required values:

```env
# Docker image
DOCKERHUB_NAMESPACE=your-dockerhub-user
DOCKERHUB_REPOSITORY=yt_api_elt
IMAGE_TAG=1.0.0

# Shared Postgres container connection
POSTGRES_CONN_USERNAME=postgres
POSTGRES_CONN_PASSWORD=your-postgres-password
POSTGRES_CONN_HOST=postgres
POSTGRES_CONN_PORT=5432

# Airflow metadata database
METADATA_DATABASE_NAME=airflow_metadata_db
METADATA_DATABASE_USERNAME=airflow_meta_user
METADATA_DATABASE_PASSWORD=your-metadata-password

# Celery result backend database
CELERY_BACKEND_NAME=celery_results_db
CELERY_BACKEND_USERNAME=celery_user
CELERY_BACKEND_PASSWORD=your-celery-password

# ELT database
ELT_DATABASE_NAME=elt_db
ELT_DATABASE_USERNAME=yt_api_user
ELT_DATABASE_PASSWORD=your-elt-password

# Airflow
AIRFLOW_UID=50000
AIRFLOW_WWW_USER_USERNAME=airflow
AIRFLOW_WWW_USER_PASSWORD=airflow
FERNET_KEY=your-fernet-key

# YouTube
API_KEY=your-youtube-data-api-key
CHANNEL_HANDLE=ArjanCodes
```

## Build and Run

Install or rebuild dependencies from `requirements.txt` by rebuilding the custom Airflow image whenever dependencies change.

Build the custom Airflow image:

```powershell
docker build -t your-dockerhub-user/yt_api_elt:1.0.0 .
```

Start the local stack:

```powershell
docker compose up -d
```

Check containers:

```powershell
docker ps
```

Open Airflow:

```text
http://localhost:8080
```

Use the Airflow username and password from `.env`.

Stop the stack:

```powershell
docker compose down
```

## Running the DAGs

In the Airflow UI:

1. Open `http://localhost:8080`.
2. Enable `youtube_video_stats`.
3. Enable `update_db`.
4. Enable `data_quality_checks`.
5. Trigger `youtube_video_stats`.

The normal chained run is:

```text
youtube_video_stats -> update_db -> data_quality_checks
```

You can still trigger `update_db` or `data_quality_checks` manually for testing or backfills.

The database update DAG expects a file named like:

```text
data/video_details_<YYYY-MM-DD>.json
```

The data quality DAG expects the `staging.yt_api` and `core.yt_api` tables to already exist, so run `update_db` before running `data_quality_checks`.

## Airflow Connections and Variables

Docker Compose injects the Airflow connection and variables from `.env`:

- `AIRFLOW_CONN_POSTGRES_DB_YT_ELT` points to the ELT PostgreSQL database.
- `AIRFLOW_VAR_API_KEY` stores the YouTube Data API key.
- `AIRFLOW_VAR_CHANNEL_HANDLE` stores the target YouTube channel handle.

The DAG code reads these through Airflow's `PostgresHook` and `Variable.get()`.

## Inspecting Data in PostgreSQL

Open a shell inside the Postgres container:

```powershell
docker exec -it postgres bash
```

Connect to the ELT database:

```bash
psql -U "$ELT_DATABASE_USERNAME" -d "$ELT_DATABASE_NAME"
```

List schemas and tables:

```sql
\dn
\dt staging.*
\dt core.*
```

Preview data:

```sql
SELECT * FROM staging.yt_api LIMIT 10;
SELECT * FROM core.yt_api LIMIT 10;
```

Count rows:

```sql
SELECT COUNT(*) FROM staging.yt_api;
SELECT COUNT(*) FROM core.yt_api;
```

From PowerShell, you can run a query directly:

```powershell
docker exec -it postgres bash -c 'psql -U "$ELT_DATABASE_USERNAME" -d "$ELT_DATABASE_NAME" -c "SELECT * FROM core.yt_api LIMIT 10;"'
```

## Useful Docker Commands

```powershell
docker compose up -d
docker compose down
docker ps
docker logs airflow-scheduler
docker logs airflow-worker
docker logs airflow-webserver
docker exec -it airflow-scheduler bash
docker exec -it postgres bash
```

## Security Notes

The `.env` file may contain database passwords, Airflow credentials, and a YouTube API key. Keep it out of version control and rotate any credentials that were committed or shared accidentally.
