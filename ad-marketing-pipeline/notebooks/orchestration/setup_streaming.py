# Databricks notebook source
import sys
sys.path.append('/Workspace/path/to/your/project/src')

from config.settings import EventHubConfig, DatabaseConfig
from streaming.event_hub_streamer import EventHubStreamer
import logging

# COMMAND ----------

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize configurations
eh_config = EventHubConfig()
db_config = DatabaseConfig()

# Initialize streamer
streamer = EventHubStreamer(spark, eh_config, db_config)

# Start streaming
logger.info("Starting Event Hub streaming...")
query = streamer.start_streaming()

# Keep the stream running
query.awaitTermination()