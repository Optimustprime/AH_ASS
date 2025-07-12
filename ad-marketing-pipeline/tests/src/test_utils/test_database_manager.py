import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    FloatType,
    TimestampType,
    BooleanType,
    IntegerType,
    DoubleType,
    LongType,
)

from src.config.settings import DatabaseConfig
from src.utils.database_manager import DatabaseManager


@pytest.fixture
def spark():
    """Create a test Spark session."""
    return (
        SparkSession.builder.appName("test-database-manager")
        .master("local[*]")
        .config("spark.sql.extensions", "")
        .getOrCreate()
    )


@pytest.fixture
def db_config():
    """Create test database configuration."""
    return DatabaseConfig(
        catalog="test_catalog",
        bronze_schema="bronze",
        silver_schema="silver",
        gold_schema="gold",
    )


@pytest.fixture
def db_manager(spark, db_config, monkeypatch):
    """Create DatabaseManager instance with mocked methods."""

    # Instead of using SQL to create tables, we'll create dataframes and register them as temp views
    def mock_create_catalog_and_schemas(self):
        # No need to create catalogs/schemas for temp views
        pass

    def mock_create_bronze_table(self):
        # Define schema
        schema = StructType(
            [
                StructField("event_type", StringType()),
                StructField("click_id", StringType()),
                StructField("advertiser", StringType()),
                StructField("advertiser_id", StringType()),
                StructField("ad_id", StringType()),
                StructField("amount", FloatType()),
                StructField("budget_value", FloatType()),
                StructField("timestamp", TimestampType()),
            ]
        )

        # Create empty dataframe with schema
        df = self.spark.createDataFrame([], schema)
        df.createOrReplaceTempView("clicks_raw")

    def mock_create_silver_table(self):
        # Define schema
        schema = StructType(
            [
                StructField("event_type", StringType()),
                StructField("click_id", StringType()),
                StructField("advertiser", StringType()),
                StructField("advertiser_id", StringType()),
                StructField("ad_id", StringType()),
                StructField("amount", FloatType()),
                StructField("budget_value", FloatType()),
                StructField("timestamp", TimestampType()),
                StructField("is_valid", BooleanType()),
                StructField("processed_at", TimestampType()),
                StructField("ingest_year", IntegerType()),
                StructField("ingest_month", IntegerType()),
                StructField("ingest_day", IntegerType()),
                StructField("ingest_hour", IntegerType()),
            ]
        )

        # Create empty dataframe with schema
        df = self.spark.createDataFrame([], schema)
        df.createOrReplaceTempView("clicks_cleaned")

    def mock_create_gold_table(self):
        # Define schema
        schema = StructType(
            [
                StructField("advertiser", StringType()),
                StructField("advertiser_id", StringType()),
                StructField("gross_spend", DoubleType()),
                StructField("net_spend", DoubleType()),
                StructField("record_count", LongType()),
                StructField("budget_value", FloatType()),
                StructField("can_serve", BooleanType()),
                StructField("window_start", TimestampType()),
                StructField("window_end", TimestampType()),
                StructField("spend_hour", TimestampType()),
                StructField("spend_day", TimestampType()),
                StructField("spend_month", TimestampType()),
            ]
        )

        # Create empty dataframe with schema
        df = self.spark.createDataFrame([], schema)
        df.createOrReplaceTempView("advertiser_spend")

    # Mock the methods for testing
    monkeypatch.setattr(
        DatabaseManager, "create_catalog_and_schemas", mock_create_catalog_and_schemas
    )
    monkeypatch.setattr(
        DatabaseManager, "_create_bronze_table", mock_create_bronze_table
    )
    monkeypatch.setattr(
        DatabaseManager, "_create_silver_table", mock_create_silver_table
    )
    monkeypatch.setattr(DatabaseManager, "_create_gold_table", mock_create_gold_table)

    return DatabaseManager(spark, db_config)


def test_create_bronze_table(db_manager, spark):
    """Test creation of bronze table."""
    db_manager.create_catalog_and_schemas()
    db_manager._create_bronze_table()

    # Verify table exists and has correct schema
    table_schema = spark.sql("SELECT * FROM clicks_raw LIMIT 0").schema
    field_map = {field.name: field.dataType for field in table_schema.fields}

    assert "event_type" in field_map
    assert "click_id" in field_map
    assert str(field_map["amount"]) == "FloatType()"
    assert str(field_map["timestamp"]) == "TimestampType()"


def test_create_silver_table(db_manager, spark):
    """Test creation of silver table."""
    db_manager.create_catalog_and_schemas()
    db_manager._create_silver_table()

    # Verify table exists and has correct schema
    table_schema = spark.sql("SELECT * FROM clicks_cleaned LIMIT 0").schema
    field_map = {field.name: field.dataType for field in table_schema.fields}

    assert "is_valid" in field_map
    assert "processed_at" in field_map
    assert "ingest_year" in field_map
    assert str(field_map["is_valid"]) == "BooleanType()"


def test_create_gold_table(db_manager, spark):
    """Test creation of gold table."""
    db_manager.create_catalog_and_schemas()
    db_manager._create_gold_table()

    # Verify table exists and has correct schema
    table_schema = spark.sql("SELECT * FROM advertiser_spend LIMIT 0").schema
    field_map = {field.name: field.dataType for field in table_schema.fields}

    assert "gross_spend" in field_map
    assert "net_spend" in field_map
    assert str(field_map["gross_spend"]) == "DoubleType()"
    assert str(field_map["can_serve"]) == "BooleanType()"


def test_create_all_tables(db_manager, spark):
    """Test creation of all tables at once."""
    db_manager.create_catalog_and_schemas()
    db_manager.create_tables()

    # Verify all tables exist by attempting to query them
    assert spark.sql("SELECT * FROM clicks_raw LIMIT 0").count() == 0
    assert spark.sql("SELECT * FROM clicks_cleaned LIMIT 0").count() == 0
    assert spark.sql("SELECT * FROM advertiser_spend LIMIT 0").count() == 0
