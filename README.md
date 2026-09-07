# YT_ELT

YouTube ELT pipeline built with Apache Airflow, Docker Compose, PostgreSQL, and Soda data quality checks.

The project extracts video metadata and statistics from the YouTube Data API, writes the raw response to a dated JSON file, loads the data into PostgreSQL, transforms it from a staging layer into a core layer, and validates both layers with Soda. The Airflow flow is chained as:

```text
youtube_video_stats -> update_db -> data_quality_checks
```

## Stack

- Apache Airflow 2.9.2
- Python 3.10
- PostgreSQL 13
- Docker Compose
- YouTube Data API v3
- Soda Core for PostgreSQL
- Pytest

## Project Structure

```text
.
|-- .github/workflows/
|   `-- ci-cd_yt-elt.yaml              # GitHub Actions CI/CD workflow
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
|-- data/                               # Extracted JSON snapshots
|-- docker/postgres/
|   `-- init-multiple-databases.sh      # Creates Airflow, Celery, and ELT databases
|-- include/soda/
|   |-- configuration.yml               # Soda PostgreSQL datasource config
|   `-- checks.yml                      # Soda checks for yt_api tables
|-- tests/
|   |-- conftest.py                     # Pytest fixtures
|   |-- integration_test.py             # API and PostgreSQL integration checks
|   `-- unit_test.py                    # Variable, connection, and DAG integrity tests
|-- docker-compose.yaml                 # Airflow stack
|-- Dockerfile                          # Custom Airflow image
`-- requirements.txt                    # Extra Python dependencies
```

## Pipeline

The project defines three Airflow DAGs in `dags/main.py`. The DAGs use the `Europe/Belgrade` timezone, start from `2026-07-31`, disable catchup, and allow one active run at a time.

### `youtube_video_stats`

Runs daily at `14:00` in the configured DAG timezone.

1. Gets the channel upload playlist ID.
2. Gets video IDs from the playlist.
3. Fetches video details from the YouTube Data API.
4. Saves records to `data/video_details_<YYYY-MM-DD>.json`.
5. Triggers `update_db`.

### `update_db`

Runs manually or when triggered by `youtube_video_stats`.

1. Reads the current dated JSON file from `data/`.
2. Creates the `staging` schema and `staging.yt_api` table if needed.
3. Inserts or updates raw YouTube records in staging.
4. Creates the `core` schema and `core.yt_api` table if needed.
5. Transforms staging records into the core table.
6. Deletes core rows that no longer exist in the latest source file.
7. Triggers `data_quality_checks`.

### `data_quality_checks`

Runs manually or when triggered by `update_db`.

1. Runs Soda checks against `staging.yt_api`.
2. Runs Soda checks against `core.yt_api`.

## Data

Extracted files are saved as:

```text
data/video_details_<YYYY-MM-DD>.json
```

The latest checked-in snapshot is:

```text
data/video_details_2026-09-07.json
```

`update_db` expects a JSON file for the current run date. Run `youtube_video_stats` first if today's file does not exist yet.

## Database Tables

### `staging.yt_api`

Raw API-shaped data using warehouse column names:

- `Video_ID`
- `Video_Title`
- `Upload_Date`
- `Duration`
- `Video_Views`
- `Likes_Count`
- `Comment_Count`

### `core.yt_api`

Transformed records used for analytics:

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

## Data Quality

Soda uses `include/soda/configuration.yml` and `include/soda/checks.yml`. The same checks file is reused for staging and core by passing `SCHEMA=staging` or `SCHEMA=core` from the Airflow task.

Current checks:

- `Video_ID` must not be missing.
- `Video_ID` must not be duplicated.
- `Likes_Count` must not be greater than `Video_Views`.
- `Comment_Count` must not be greater than `Video_Views`.

## Environment Variables

Create a `.env` file in the project root for local development. Do not commit real credentials or API keys.

```env
# Docker image
DOCKERHUB_NAMESPACE=your-dockerhub-user
DOCKERHUB_USERNAME=your-dockerhub-user
DOCKERHUB_REPOSITORY=yt_api_elt

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

Docker Compose injects these into Airflow as:

- `AIRFLOW_CONN_POSTGRES_DB_YT_ELT`
- `AIRFLOW_VAR_API_KEY`
- `AIRFLOW_VAR_CHANNEL_HANDLE`

## Build and Run Locally

Build the custom Airflow image:

```powershell
docker build -t your-dockerhub-user/yt_api_elt:latest .
```

Start the Airflow stack:

```powershell
docker compose up -d --wait
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

For local debugging, run a DAG test from the scheduler container:

```powershell
docker exec -it airflow-scheduler airflow dags test youtube_video_stats
docker exec -it airflow-scheduler airflow dags test update_db
docker exec -it airflow-scheduler airflow dags test data_quality_checks
```

Before testing chained DAGs, make sure Airflow has registered all DAGs:

```powershell
docker exec -it airflow-scheduler airflow dags reserialize
docker exec -it airflow-scheduler airflow dags list
```

## Tests

Run tests inside the Airflow scheduler container:

```powershell
docker exec -it airflow-scheduler pytest /opt/airflow/tests -v
```

Or run them locally after installing dependencies and setting the required environment variables:

```powershell
pytest tests -v
```

The integration tests require a valid YouTube API key and a reachable PostgreSQL database.

## CI/CD

GitHub Actions is configured in `.github/workflows/ci-cd_yt-elt.yaml`.

The workflow runs on pushes to `main`, pushes to `feature/**`, pull requests to `main`, and manual `workflow_dispatch` runs.

Jobs:

- `build-and-push-image` builds and pushes the custom Airflow image when `Dockerfile`, `requirements.txt`, or `src/**` changes, or when the workflow is run manually.
- `unit-and-integration-and-e2e-tests` starts Docker Compose, waits for services, reserializes/registers DAGs, runs Pytest, runs `airflow dags test` for all three DAGs, and tears the stack down.

The test job runs when `dags/**`, `include/**`, `tests/**`, `requirements.txt`, or `docker-compose.yaml` changes, or when the workflow is run manually.

Required GitHub repository variables:

- `AIRFLOW_UID`
- `CHANNEL_HANDLE`
- `DOCKERHUB_NAMESPACE`
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_REPOSITORY`

Required GitHub repository secrets:

- `AIRFLOW_WWW_USER_USERNAME`
- `AIRFLOW_WWW_USER_PASSWORD`
- `API_KEY`
- `CELERY_BACKEND_NAME`
- `CELERY_BACKEND_USERNAME`
- `CELERY_BACKEND_PASSWORD`
- `ELT_DATABASE_NAME`
- `ELT_DATABASE_USERNAME`
- `ELT_DATABASE_PASSWORD`
- `FERNET_KEY`
- `METADATA_DATABASE_NAME`
- `METADATA_DATABASE_USERNAME`
- `METADATA_DATABASE_PASSWORD`
- `POSTGRES_CONN_USERNAME`
- `POSTGRES_CONN_PASSWORD`
- `POSTGRES_CONN_HOST`
- `POSTGRES_CONN_PORT`
- `DOCKERHUB_PASSWORD`

## Inspecting PostgreSQL

Open a shell inside the Postgres container:

```powershell
docker exec -it postgres bash
```

Connect to the ELT database:

```bash
psql -U "$ELT_DATABASE_USERNAME" -d "$ELT_DATABASE_NAME"
```

Useful SQL:

```sql
\dn
\dt staging.*
\dt core.*
SELECT * FROM staging.yt_api LIMIT 10;
SELECT * FROM core.yt_api LIMIT 10;
SELECT COUNT(*) FROM staging.yt_api;
SELECT COUNT(*) FROM core.yt_api;
```

Run a query directly from PowerShell:

```powershell
docker exec -it postgres bash -c 'psql -U "$ELT_DATABASE_USERNAME" -d "$ELT_DATABASE_NAME" -c "SELECT * FROM core.yt_api LIMIT 10;"'
```

## Useful Docker Commands

```powershell
docker compose up -d --wait
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
