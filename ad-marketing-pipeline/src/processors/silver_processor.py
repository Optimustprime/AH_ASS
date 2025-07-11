from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, year, month, dayofmonth, hour, current_timestamp
from datetime import datetime, timedelta
from typing import Optional
import logging
import sys
sys.path.append('/Workspace/Users/Project/AH_ASS/ad-marketing-pipeline/src')
from config.settings import DatabaseConfig

class SilverProcessor:
    """Processes bronze data to silver layer with data cleaning and validation."""

    def __init__(self, spark: SparkSession, db_config: DatabaseConfig):
        """
        Initialize the silver processor.

        Args:
            spark: Spark session
            db_config: Database configuration
        """
        self.spark = spark
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)

    def read_bronze_data(self, start_ts: datetime, end_ts: datetime) -> DataFrame:
        """
        Read bronze data for a specific time window.

        Args:
            start_ts: Start timestamp
            end_ts: End timestamp

        Returns:
            Filtered DataFrame from bronze table
        """
        bronze_df = self.spark.read.table(self.db_config.bronze_table)

        filtered_df = bronze_df.filter(
            (col("timestamp") >= start_ts) &
            (col("timestamp") < end_ts)
        )

        record_count = filtered_df.count()
        self.logger.info(f"Records fetched from Bronze: {record_count}")

        return filtered_df

    def clean_and_transform(self, df: DataFrame) -> DataFrame:
        """
        Clean and transform bronze data for silver layer.

        Args:
            df: Raw bronze DataFrame

        Returns:
            Cleaned DataFrame ready for silver layer
        """
        silver_df = df \
            .filter(col("event_type") == "ad_click") \
            .filter(col("amount").isNotNull() & (col("amount") > 0)) \
            .filter(col("advertiser_id").isNotNull()) \
            .withColumn("is_valid", col("amount") > 0) \
            .withColumn("processed_at", current_timestamp()) \
            .withColumn("ingest_year", year(col("timestamp"))) \
            .withColumn("ingest_month", month(col("timestamp"))) \
            .withColumn("ingest_day", dayofmonth(col("timestamp"))) \
            .withColumn("ingest_hour", hour(col("timestamp")))

        return silver_df

    def write_to_silver(self, df: DataFrame) -> None:
        """
        Write processed data to silver table.

        Args:
            df: Cleaned DataFrame to write
        """
        df.write \
            .format("delta") \
            .mode("append") \
            .partitionBy("ingest_year", "ingest_month", "ingest_day") \
            .saveAsTable(self.db_config.silver_table)

        self.logger.info(f"Data written to {self.db_config.silver_table}")

    def process_hour(self, target_hour: Optional[datetime] = None) -> None:
        """
        Process a specific hour of data from bronze to silver.

        Args:
            target_hour: Target hour to process (defaults to current hour)
        """
        if target_hour is None:
            target_hour = datetime.utcnow()

        start_ts = target_hour.replace(minute=0, second=0, microsecond=0)
        end_ts = start_ts + timedelta(hours=1)

        self.logger.info(f"Processing hour: {start_ts} to {end_ts}")

        bronze_df = self.read_bronze_data(start_ts, end_ts)

        if bronze_df.count() == 0:
            self.logger.warning("No records found for the specified hour. Exiting.")
            return

        silver_df = self.clean_and_transform(bronze_df)
        self.write_to_silver(silver_df)