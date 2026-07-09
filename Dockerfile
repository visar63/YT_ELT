ARG AIRFLOW_VERSION=2.9.2
ARG PYTHON_VERSION=3.10

FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

ENV AIRFLOW_HOME=/opt/airflow

COPY requirements.txt /

RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt



# FROM python:3.13-slim

# WORKDIR /app

# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY video_stats.py .
# RUN mkdir -p data

# CMD ["python", "video_stats.py"]