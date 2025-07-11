# Databricks notebook source
from datetime import datetime, timedelta
from pyspark.sql.functions import (
    col, year, month, dayofmonth, hour,
    current_timestamp
)
import logging

# COMMAND ----------


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger("bronze_to_silver")


now = datetime.utcnow()
prev_hour = now

y, m, d, h = prev_hour.year, prev_hour.month, prev_hour.day, prev_hour.hour
logger.info(f"Processing hour: {y}-{m:02}-{d:02} {h:02}:00")

# COMMAND ----------

logger.info("Reading Bronze table...")
bronze_df = spark.read.table("ad_marketing_catalog.bronze.ad_click_events_raw")

start_ts = prev_hour.replace(minute=0, second=0, microsecond=0)
end_ts = start_ts + timedelta(hours=1)

filtered_df = bronze_df.filter(
    (col("timestamp") >= start_ts) & 
    (col("timestamp") < end_ts)
)
filtered_df.display()


# COMMAND ----------

record_count = filtered_df.count()
logger.info(f"Records fetched from Bronze: {record_count}")

if record_count == 0:
    logger.warning("No records found for the specified hour. Exiting.")
else:
    #Step 3: Clean Data (Silver Transformations)
    logger.info("Cleaning and preparing data for Silver...")

    silver_df = filtered_df \
        .filter(col("event_type") == "ad_click") \
        .filter(col("amount").isNotNull() & (col("amount") > 0)) \
        .filter(col("advertiser_id").isNotNull()) \
        .withColumn("is_valid", col("amount") > 0) \
        .withColumn("processed_at", current_timestamp()) \
        .withColumn("ingest_year", year(col("timestamp"))) \
        .withColumn("ingest_month", month(col("timestamp"))) \
        .withColumn("ingest_day", dayofmonth(col("timestamp"))) \
        .withColumn("ingest_hour", hour(col("timestamp")))

    # Step 4: Write to Silver Table
    logger.info("Writing to Silver table...")

    silver_df.write \
        .format("delta") \
        .mode("append") \
        .partitionBy("ingest_year", "ingest_month", "ingest_day") \
        .saveAsTable("ad_marketing_catalog.silver.ad_click_events_clean")
