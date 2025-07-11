from pyspark.sql import SparkSession
from typing import Dict, List
import logging

from ..config.settings import DatabaseConfig

class DatabaseManager:
    """Manages database operations and table provisioning."""

    def __init__(self, spark: SparkSession, db_config: DatabaseConfig):
        """
        Initialize the database manager.

        Args:
            spark: Spark session
            db_config: Database configuration
        """
        self.spark = spark
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)

    def create_catalog_and_schemas(self) -> None:
        """Create catalog and schemas if they don't exist."""
        commands = [
            f"CREATE CATALOG IF NOT EXISTS {self.db_config.catalog}",
            f"USE CATALOG {self.db_config.catalog}",
            f"CREATE SCHEMA IF NOT EXISTS {self.db_config.bronze_schema}",
            f"CREATE SCHEMA IF NOT EXISTS {self.db_config.silver_schema}",
            f"CREATE SCHEMA IF NOT EXISTS {self.db_config.gold_schema}"
        ]

        for cmd in commands:
            self.spark.sql(cmd)
            self.logger.info(f"Executed: {cmd}")

    def create_tables(self) -> None:
        """Create all required tables."""
        self._create_bronze_table()
        self._create_silver_table()
        self._create_gold_table()

    def _create_bronze_table(self) -> None:
        """Create bronze table for raw ad click events."""
        sql = f"""
        CREATE TABLE IF NOT EXISTS {self.db_config.bronze_table} (
            event_type STRING,
            click_id STRING,
            advertiser_id STRING,
            ad_id STRING,
            amount FLOAT,
            budget_value FLOAT,
            timestamp TIMESTAMP
        )
        USING DELTA
        """
        self.spark.sql(sql)
        self.logger.info(f"Created bronze table: {self.db_config.bronze_table}")

    def _create_silver_table(self) -> None:
        """Create silver table for cleaned ad click events."""
        sql = f"""
        CREATE TABLE IF NOT EXISTS {self.db_config.silver_table} (
            event_type STRING,
            click_id STRING,
            advertiser_id STRING,
            ad_id STRING,
            amount FLOAT,
            budget_value FLOAT,
            timestamp TIMESTAMP,
            is_valid BOOLEAN,
            processed_at TIMESTAMP,
            ingest_year INT,
            ingest_month INT,
            ingest_day INT,
            ingest_hour INT
        )
        USING DELTA
        PARTITIONED BY (ingest_year, ingest_month, ingest_day)
        """
        self.spark.sql(sql)
        self.logger.info(f"Created silver table: {self.db_config.silver_table}")

    def _create_gold_table(self) -> None:
        """Create gold table for aggregated advertiser spend."""
        sql = f"""
        CREATE TABLE IF NOT EXISTS {self.db_config.gold_table} (
            advertiser_id STRING,
            gross_spend DOUBLE,
            net_spend DOUBLE,
            record_count BIGINT,
            budget_value FLOAT,
            can_serve BOOLEAN,
            window_start TIMESTAMP,
            window_end TIMESTAMP,
            spend_hour TIMESTAMP,
            spend_day TIMESTAMP,
            spend_month TIMESTAMP
        )
        USING DELTA
        PARTITIONED BY (spend_day)
        """
        self.spark.sql(sql)
        self.logger.info(f"Created gold table: {self.db_config.gold_table}")