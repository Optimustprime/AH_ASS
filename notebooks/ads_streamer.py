# Databricks notebook source
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, expr
from pyspark.sql.types import StructType, StringType, FloatType, TimestampType

# Define Event Hub connection details
event_hub_connection_string = dbutils.secrets.get(scope="ahass-scope", key="EVENT_HUB_CONNECTION_STRING")
event_hub_name = "<EVENT_HUB_NAME>"

# Create Spark session
spark = SparkSession.builder.appName("EventHubConsumer").getOrCreate()

# Event Hub configuration
eh_conf = {
    'eventhubs.connectionString': f"Endpoint=sb://<NAMESPACE>.servicebus.windows.net/;SharedAccessKeyName=<KEY_NAME>;SharedAccessKey=<KEY>;EntityPath={event_hub_name}"
}

# Define schema for the incoming data
schema = StructType() \
    .add("event_type", StringType()) \
    .add("click_id", StringType()) \
    .add("advertiser_id", StringType()) \
    .add("ad_id", StringType()) \
    .add("amount", FloatType()) \
    .add("budget_value", FloatType()) \
    .add("timestamp", TimestampType())

# Read from Event Hub
df = spark.readStream \
    .format("eventhubs") \
    .options(**eh_conf) \
    .load()

# Parse the JSON data
parsed_df = df.selectExpr("CAST(body AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*")

# Write to console for debugging
query = parsed_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

query.awaitTermination()
