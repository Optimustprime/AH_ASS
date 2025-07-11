# Databricks notebook source
from pyspark.sql.functions import col, sum, count, when, lit, max as spark_max, date_trunc
from datetime import datetime, timedelta



# COMMAND ----------

now = datetime.utcnow()
prev_hour = now - timedelta(hours=4)
start_ts = prev_hour.replace(minute=0, second=0, microsecond=0)
end_ts = start_ts + timedelta(hours=1)
print(start_ts, end_ts)

silver_df = spark.read.table("ad_marketing_catalog.silver.ad_click_events_clean")

filtered_df = silver_df.filter(
    (col("timestamp") >= start_ts) &
    (col("timestamp") < end_ts)
)

filtered_df.display()


# COMMAND ----------


gold_df = filtered_df.groupBy("advertiser_id").agg(
    sum("amount").alias("gross_spend"),
    sum(when(col("is_valid") == True, col("amount")).otherwise(0)).alias("net_spend"),
    count("*").alias("record_count"),
    spark_max("budget_value").alias("budget_value")
).withColumn("window_start", lit(start_ts)) \
 .withColumn("window_end", lit(end_ts)) \
 .withColumn("can_serve", col("net_spend") < col("budget_value")) \
 .withColumn("spend_hour", date_trunc("HOUR", lit(start_ts))) \
 .withColumn("spend_day", date_trunc("DAY", lit(start_ts))) \
 .withColumn("spend_month", date_trunc("MONTH", lit(start_ts)))


gold_df.write \
    .format("delta") \
    .mode("append") \
    .partitionBy("spend_day") \
    .saveAsTable("ad_marketing_catalog.gold.advertiser_spend")

