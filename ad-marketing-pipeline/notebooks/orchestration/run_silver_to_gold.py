# Databricks notebook source
import sys

sys.path.append("/Workspace/Users/Project/AH_ASS/ad-marketing-pipeline/src")

from config.settings import DatabaseConfig
from processors.gold_processor import GoldProcessor
import logging

# COMMAND ----------

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize configuration
db_config = DatabaseConfig()

# Initialize processor
processor = GoldProcessor(spark, db_config)

# Process current hour (4 hours back)
logger.info("Starting silver to gold processing...")
processor.process_hour()
logger.info("Silver to gold processing completed.")
