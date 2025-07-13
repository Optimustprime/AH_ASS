# Ad Marketing Pipeline

A real-time data pipeline for ad marketing budget management using Apache Spark, Delta Lake, and Azure Event Hubs on Databricks.


# Architecture Overview
![Ad Marketing Pipeline Architecture](assets/AH-Page-1.drawio.png)

## Overview

This pipeline processes ad click events in real-time to track advertiser spending against budgets and make serving decisions. It follows the medallion architecture pattern with Bronze, Silver, and Gold layers.

## Documentation

For detailed API documentation, see:

- [Processors](api-reference/processors.md)
- [Streaming](api-reference/streaming.md)
- [Configuration](api-reference/config.md)

## Notebooks

Key notebooks used in this pipeline:

### Orchestration
- [Bronze to Silver Processing](api-reference/run_bronze_to_silver.md)
- [Silver to Gold Processing](api-reference/run_silver_to_gold.md)
- [Setup Streaming](api-reference/setup_streaming.md)

### Setup
- [Provision Tables](api-reference/provision_tables.md)

## Schema Diagram

![Schema](assets/schema.png)

## Backend Schema Diagram

![Schema](assets/backendschema.png)

## Dashboards
![Dashboards](assets/dashboard1.png)
![Dashboards](assets/dashboard2.png)
![Dashboards](assets/dashboard3.png)
![Dashboards](assets/dashboard4.png)
![Dashboards](assets/dashboard5.png)


