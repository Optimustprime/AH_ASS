from pyspark.sql.types import (
    StructType,
    StringType,
    FloatType,
    TimestampType,
    BooleanType,
    IntegerType,
    LongType,
    DoubleType,
)


class AdClickSchemas:
    """Schema definitions for ad click events across different layers."""

    @staticmethod
    def bronze_schema() -> StructType:
        """Schema for bronze layer ad click events."""
        return (
            StructType()
            .add("event_type", StringType())
            .add("click_id", StringType())
            .add("advertiser", StringType())
            .add("advertiser_id", StringType())
            .add("ad_id", StringType())
            .add("amount", FloatType())
            .add("budget_value", FloatType())
            .add("timestamp", TimestampType())
        )

    @staticmethod
    def silver_schema() -> StructType:
        """Schema for silver layer cleaned ad click events."""
        return (
            StructType()
            .add("event_type", StringType())
            .add("click_id", StringType())
            .add("advertiser", StringType())
            .add("advertiser_id", StringType())
            .add("ad_id", StringType())
            .add("amount", FloatType())
            .add("budget_value", FloatType())
            .add("timestamp", TimestampType())
            .add("is_valid", BooleanType())
            .add("processed_at", TimestampType())
            .add("ingest_year", IntegerType())
            .add("ingest_month", IntegerType())
            .add("ingest_day", IntegerType())
            .add("ingest_hour", IntegerType())
        )

    @staticmethod
    def gold_schema() -> StructType:
        """Schema for gold layer aggregated advertiser spend."""
        return (
            StructType()
            .add("advertiser", StringType())
            .add("advertiser_id", StringType())
            .add("gross_spend", DoubleType())
            .add("net_spend", DoubleType())
            .add("record_count", LongType())
            .add("budget_value", FloatType())
            .add("can_serve", BooleanType())
            .add("window_start", TimestampType())
            .add("window_end", TimestampType())
            .add("spend_hour", TimestampType())
            .add("spend_day", TimestampType())
            .add("spend_month", TimestampType())
        )
