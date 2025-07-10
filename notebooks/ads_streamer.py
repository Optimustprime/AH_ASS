# Databricks notebook source
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, FloatType, TimestampType

# Fetch Event Hub connection string from Databricks secret scope
event_hub_connection_string = dbutils.secrets.get(scope="ahass-scope", key="EVENT_HUB_CONNECTION_STRING")
event_hub_name = "ad-clicks"  # Update with your actual Event Hub name

# Create Spark session
spark = SparkSession.builder.appName("EventHubConsumer").getOrCreate()

# Event Hub configuration
eh_conf = {
    'eventhubs.connectionString': f"{event_hub_connection_string};EntityPath={event_hub_name}"
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

# Read from Event Hub as a streaming DataFrame
df = spark.readStream \
    .format("eventhubs") \
    .options(**eh_conf) \
    .load()

# Parse the JSON data from the Event Hub message body
parsed_df = df.selectExpr("CAST(body AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*")

# Write the streaming data to the console (for debugging)
query = parsed_df.writeStream \
    .outputMode("append") \
    .format("console") \
    .option("truncate", False) \
    .start()

query.awaitTermination()
