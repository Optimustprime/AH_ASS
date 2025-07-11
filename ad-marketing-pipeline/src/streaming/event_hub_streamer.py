from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, from_json
from pyspark.sql.streaming import StreamingQuery
from typing import Dict, Any
import logging

from ..config.settings import EventHubConfig, DatabaseConfig
from ..models.schemas import AdClickSchemas


class EventHubStreamer:
    """Handles streaming data from Event Hub to Delta tables."""

    def __init__(self, spark: SparkSession, eh_config: EventHubConfig, db_config: DatabaseConfig):
        """
        Initialize the Event Hub streamer.

        Args:
            spark: Spark session
            eh_config: Event Hub configuration
            db_config: Database configuration
        """
        self.spark = spark
        self.eh_config = eh_config
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)

    def _get_event_hub_config(self) -> Dict[str, Any]:
        """Get Event Hub connection configuration."""
        connection_string = self.spark.sparkContext._jvm.org.apache.spark.sql.functions.dbutils.secrets.get(
            scope=self.eh_config.scope,
            key=self.eh_config.connection_string_key
        )

        return {
            'eventhubs.connectionString': self.spark.sparkContext._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt(
                connection_string),
            'eventhubs.name': self.eh_config.event_hub_name
        }

    def create_streaming_dataframe(self) -> DataFrame:
        """
        Create a streaming DataFrame from Event Hub.

        Returns:
            Streaming DataFrame with parsed ad click events
        """
        eh_conf = self._get_event_hub_config()

        # Read from Event Hub
        raw_df = self.spark.readStream \
            .format("eventhubs") \
            .options(**eh_conf) \
            .load()

        # Parse JSON data
        schema = AdClickSchemas.bronze_schema()
        parsed_df = raw_df.selectExpr("CAST(body AS STRING) as json") \
            .select(from_json(col("json"), schema).alias("data")) \
            .select("data.*")

        return parsed_df

    def start_streaming(self) -> StreamingQuery:
        """
        Start streaming from Event Hub to bronze table.

        Returns:
            StreamingQuery object for monitoring
        """
        streaming_df = self.create_streaming_dataframe()

        query = streaming_df.writeStream \
            .format("delta") \
            .outputMode("append") \
            .option("checkpointLocation", self.eh_config.checkpoint_location) \
            .table(self.db_config.bronze_table)

        self.logger.info(f"Started streaming to {self.db_config.bronze_table}")
        return query
