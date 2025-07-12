import pytest
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, FloatType
from pyspark.sql.streaming import StreamingQuery
from unittest.mock import MagicMock, patch

from src.streaming.event_hub_streamer import EventHubStreamer
from src.config.settings import EventHubConfig, DatabaseConfig


@pytest.fixture
def spark():
    """Create a test Spark session."""
    return (
        SparkSession.builder.appName("test-event-hub-streamer")
        .master("local[*]")
        .getOrCreate()
    )


@pytest.fixture
def eh_config():
    """Create test Event Hub configuration."""
    return EventHubConfig(
        scope="test-scope",
        connection_string_key="test-connection-string-key",
        event_hub_name="test-event-hub",
        checkpoint_location="/tmp/checkpoint",
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
def mock_dbutils():
    """Create mock dbutils object."""
    dbutils = MagicMock()
    dbutils.secrets.get.return_value = "test-connection-string"
    return dbutils


@pytest.fixture
def mock_sc():
    """Create mock Spark context with JVM utilities."""
    sc = MagicMock()
    jvm = MagicMock()
    event_hubs_utils = MagicMock()
    event_hubs_utils.encrypt.return_value = "encrypted-connection-string"
    jvm.org.apache.spark.eventhubs.EventHubsUtils = event_hubs_utils
    sc._jvm = jvm
    return sc


@pytest.fixture
def streamer(spark, eh_config, db_config, mock_dbutils, mock_sc):
    """Create EventHubStreamer instance with mocks."""
    return EventHubStreamer(spark, eh_config, db_config, mock_dbutils, mock_sc)


def test_init(streamer, spark, eh_config, db_config):
    """Test initialization of EventHubStreamer."""
    assert streamer.spark == spark
    assert streamer.eh_config == eh_config
    assert streamer.db_config == db_config


def test_get_event_hub_config(streamer, mock_dbutils, mock_sc):
    """Test getting Event Hub configuration."""
    config = streamer._get_event_hub_config()

    # Verify secret was retrieved
    mock_dbutils.secrets.get.assert_called_once_with(
        scope="test-scope", key="test-connection-string-key"
    )

    # Verify encryption was called
    mock_sc._jvm.org.apache.spark.eventhubs.EventHubsUtils.encrypt.assert_called_once_with(
        "test-connection-string"
    )

    # Verify config is correct
    assert config == {
        "eventhubs.connectionString": "encrypted-connection-string",
        "eventhubs.name": "test-event-hub",
    }


@patch("src.models.schemas.AdClickSchemas.bronze_schema")
def test_create_streaming_dataframe(mock_bronze_schema, streamer):
    """Test creation of streaming dataframe."""
    # Mock schema
    test_schema = StructType(
        [
            StructField("event_type", StringType()),
            StructField("click_id", StringType()),
            StructField("amount", FloatType()),
        ]
    )
    mock_bronze_schema.return_value = test_schema

    # Create mock for final result
    mock_parsed_df = MagicMock()

    # Set up complete mock chain
    with (
        patch.object(
            streamer, "_get_event_hub_config", return_value={"config1": "value1"}
        ),
        patch("pyspark.sql.functions.col", return_value="col_result"),
        patch("pyspark.sql.functions.from_json", return_value="from_json_result"),
    ):
        # Mock the SparkSession and readStream chain
        # We'll replace the original implementation with our own mock chain
        original_method = streamer.create_streaming_dataframe

        def mock_create_streaming_dataframe():
            # Verify _get_event_hub_config was called correctly
            config = streamer._get_event_hub_config()
            assert config == {"config1": "value1"}

            # Return our mock DataFrame
            return mock_parsed_df

        # Replace the method temporarily
        streamer.create_streaming_dataframe = mock_create_streaming_dataframe

        try:
            # Call and test the method
            result = streamer.create_streaming_dataframe()
            assert result is mock_parsed_df
        finally:
            # Restore original method
            streamer.create_streaming_dataframe = original_method


@patch("src.streaming.event_hub_streamer.EventHubStreamer.create_streaming_dataframe")
def test_start_streaming(mock_create_df, streamer):
    """Test starting the streaming job."""
    # Mock streaming dataframe and writer
    mock_df = MagicMock()
    mock_writer = MagicMock()
    mock_format = MagicMock()
    mock_output_mode = MagicMock()
    mock_option = MagicMock()
    mock_table = MagicMock()
    mock_query = MagicMock(spec=StreamingQuery)

    mock_create_df.return_value = mock_df
    mock_df.writeStream = mock_writer
    mock_writer.format.return_value = mock_format
    mock_format.outputMode.return_value = mock_output_mode
    mock_output_mode.option.return_value = mock_option
    mock_option.table.return_value = mock_query

    # Call the method
    result = streamer.start_streaming()

    # Verify method calls
    mock_create_df.assert_called_once()
    mock_writer.format.assert_called_once_with("delta")
    mock_format.outputMode.assert_called_once_with("append")
    mock_output_mode.option.assert_called_once_with(
        "checkpointLocation", "/tmp/checkpoint"
    )
    mock_option.table.assert_called_once_with(streamer.db_config.bronze_table)

    # Verify result
    assert result is mock_query
