# Setup Streaming

This notebook sets up the real-time streaming from Event Hub to the bronze layer.

# Databricks notebook source
import sys
sys.path.append('/Workspace/Users/Project/AH_ASS/ad-marketing-pipeline/src')

from config.settings import EventHubConfig, DatabaseConfig
from streaming.event_hub_streamer import EventHubStreamer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize configurations
eh_config = EventHubConfig()
db_config = DatabaseConfig()

# Initialize streamer
streamer = EventHubStreamer(spark, eh_config, db_config, dbutils, sc)

# Start streaming
logger.info("Starting Event Hub streaming...")
query = streamer.start_streaming()

# Keep the stream running
query.awaitTermination()