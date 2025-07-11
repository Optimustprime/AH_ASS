from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, sum, count, when, lit, max as spark_max, date_trunc
from datetime import datetime, timedelta
from typing import Optional
import logging
import sys
sys.path.append('/Workspace/Users/Project/AH_ASS/ad-marketing-pipeline/src')
from config.settings import DatabaseConfig


class GoldProcessor:
    """Processes silver data to gold layer with business aggregations."""

    def __init__(self, spark: SparkSession, db_config: DatabaseConfig):
        """
        Initialize the gold processor.

        Args:
            spark: Spark session
            db_config: Database configuration
        """
        self.spark = spark
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)

    def read_silver_data(self, start_ts: datetime, end_ts: datetime) -> DataFrame:
        """
        Read silver data for a specific time window.

        Args:
            start_ts: Start timestamp
            end_ts: End timestamp

        Returns:
            Filtered DataFrame from silver table
        """
        silver_df = self.spark.read.table(self.db_config.silver_table)

        filtered_df = silver_df.filter(
            (col("timestamp") >= start_ts) &
            (col("timestamp") < end_ts)
        )

        return filtered_df

    def aggregate_spend_data(self, df: DataFrame, start_ts: datetime, end_ts: datetime) -> DataFrame:
        """
        Aggregate spend data by advertiser.

        Args:
            df: Silver DataFrame
            start_ts: Window start timestamp
            end_ts: Window end timestamp

        Returns:
            Aggregated DataFrame with spend metrics
        """
        gold_df = df.groupBy("advertiser").agg(
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

        return gold_df

    def write_to_gold(self, df: DataFrame) -> None:
        """
        Write aggregated data to gold table.

        Args:
            df: Aggregated DataFrame to write
        """
        df.write \
            .format("delta") \
            .mode("append") \
            .partitionBy("spend_day") \
            .saveAsTable(self.db_config.gold_table)

        self.logger.info(f"Data written to {self.db_config.gold_table}")

    def process_hour(self, target_hour: Optional[datetime] = None, hours_back: int = 4) -> None:
        """
        Process a specific hour of data from silver to gold.

        Args:
            target_hour: Target hour to process (defaults to current hour)
            hours_back: Number of hours back to process
        """
        if target_hour is None:
            target_hour = datetime.utcnow()

        start_ts = target_hour.replace(minute=0, second=0, microsecond=0)
        end_ts = start_ts + timedelta(hours=1)

        self.logger.info(f"Processing hour: {start_ts} to {end_ts}")

        silver_df = self.read_silver_data(start_ts, end_ts)
        gold_df = self.aggregate_spend_data(silver_df, start_ts, end_ts)
        self.write_to_gold(gold_df)
