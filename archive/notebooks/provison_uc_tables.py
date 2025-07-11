# Databricks notebook source
# MAGIC %sql
# MAGIC
# MAGIC CREATE CATALOG IF NOT EXISTS ad_marketing_catalog;
# MAGIC
# MAGIC USE CATALOG ad_marketing_catalog;
# MAGIC
# MAGIC CREATE SCHEMA IF NOT EXISTS bronze;
# MAGIC CREATE SCHEMA IF NOT EXISTS silver;
# MAGIC CREATE SCHEMA IF NOT EXISTS gold;
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC CREATE TABLE IF NOT EXISTS bronze.ad_click_events_raw (
# MAGIC   event_type STRING,
# MAGIC   click_id STRING,
# MAGIC   advertiser_id STRING,
# MAGIC   ad_id STRING,
# MAGIC   amount FLOAT,
# MAGIC   budget_value FLOAT,
# MAGIC   timestamp TIMESTAMP
# MAGIC )
# MAGIC USING DELTA
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC
# MAGIC CREATE TABLE silver.ad_click_events_clean (
# MAGIC   event_type      STRING,
# MAGIC   click_id        STRING,
# MAGIC   advertiser_id   STRING,
# MAGIC   ad_id           STRING,
# MAGIC   amount          FLOAT,
# MAGIC   budget_value    FLOAT,
# MAGIC   timestamp       TIMESTAMP,
# MAGIC   is_valid        BOOLEAN,
# MAGIC   processed_at    TIMESTAMP,
# MAGIC   ingest_year     INT,
# MAGIC   ingest_month    INT,
# MAGIC   ingest_day      INT,
# MAGIC   ingest_hour     INT
# MAGIC )
# MAGIC PARTITIONED BY (ingest_year, ingest_month, ingest_day)
# MAGIC

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE TABLE IF NOT EXISTS gold.advertiser_spend (
# MAGIC   advertiser_id     STRING,
# MAGIC   gross_spend       DOUBLE,
# MAGIC   net_spend         DOUBLE,
# MAGIC   record_count      BIGINT,
# MAGIC   budget_value      FLOAT,
# MAGIC   can_serve         BOOLEAN,
# MAGIC   window_start      TIMESTAMP,
# MAGIC   window_end        TIMESTAMP,
# MAGIC   spend_hour        TIMESTAMP,
# MAGIC   spend_day         TIMESTAMP,
# MAGIC   spend_month       TIMESTAMP
# MAGIC )
# MAGIC USING DELTA
# MAGIC PARTITIONED BY (spend_day);
# MAGIC
