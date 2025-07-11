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
# MAGIC CREATE TABLE IF NOT EXISTS silver.click_events (
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
# MAGIC select * from ad_marketing_catalog.bronze.ad_click_events_raw
