# Databricks notebook source
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, decode
from pyspark.sql.types import StructType, StringType, FloatType, TimestampType
import json

# COMMAND ----------

event_hub_connection_string = dbutils.secrets.get(scope="ahass-scope", key="EVENT_HUB_CONNECTION_STRING")
event_hub_name = "ad-clicks" 

eh_conf = {
  'eventhubs.connectionString': sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(event_hub_connection_string),
  'eventhubs.name': event_hub_name
}

# COMMAND ----------

schema = StructType() \
    .add("event_type", StringType()) \
    .add("click_id", StringType()) \
    .add("advertiser_id", StringType()) \
    .add("ad_id", StringType()) \
    .add("amount", FloatType()) \
    .add("budget_value", FloatType()) \
    .add("timestamp", TimestampType())

# Read from Event Hub as a streaming DataFrame
df = spark.readStream \
    .format("eventhubs") \
    .options(**eh_conf) \
    .load()

# Parse the JSON data from the Event Hub message body
parsed_df = df.selectExpr("CAST(body AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*")

# Write to Delta table
query = parsed_df.writeStream \
    .format("delta") \
    .outputMode("append") \
    .option("checkpointLocation", "/delta/checkpoints/ad_click_events_raw") \
    .table("ad_marketing_catalog.bronze.ad_click_events_raw")

query.awaitTermination()

