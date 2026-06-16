# DataTel Telecom Analytics Pipeline

## Overview
DataTel Communications is a mid-sized telecom operator that collects millions of records daily across independent billing, network, and CRM systems. Because these systems operate in isolation, the data often contains duplicates, missing values, inconsistent formats, and unreliable timestamps, making it difficult to generate accurate business insights.

This project addresses that challenge by building an end-to-end, SQL-first data engineering pipeline that transforms raw operational data into a trusted analytics layer. The pipeline consolidates disparate telecom datasets into a unified customer view that supports customer analytics, churn risk detection, and revenue operations.

## Business Problem
DataTel needed a way to answer critical business questions, including:
* **Customer analytics** — who are the most valuable users, and how do they actually engage with the network?
* **Churn risk detection** — which customers are going quiet before they cancel?
* **Revenue operations** — where does data consumption not match what customers are paying?

## Pipeline Architecture
![My local image](C:\Users\PC\Downloads\ChatGPT Image Jun 16, 2026, 11_08_03 PM.png
)

## Tech Stack
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white) ![SQL](https://img.shields.io/badge/SQL-CC2927?style=for-the-badge&logo=microsoftsqlserver&logoColor=white) ![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Apache Airflow](https://img.shields.io/badge/Apache%20Airflow-017CEE?style=for-the-badge&logo=apacheairflow&logoColor=white) ![BigQuery](https://img.shields.io/badge/BigQuery-669DF6?style=for-the-badge&logo=googlebigquery&logoColor=white) ![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

## Repository Structure
```
datatel-telecom-analytics/
├── sql/
│   ├── 01_data_quality_checks.sql
│   ├── 02_staging.sql
│   ├── 03_transformations.sql
│   ├── 04_dw_table.sql
│   ├── 05_analytical_queries.sql
│   └── 06_incremental_load.sql
├── dags/
│   └── telecom_pipeline_dag.py
├── docs/
│   └── architecture.png
└── README.md
```
