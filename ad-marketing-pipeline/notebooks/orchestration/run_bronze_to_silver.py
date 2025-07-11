# Databricks notebook source
import sys
sys.path.append('/Workspace/Users/Project/AH_ASS/ad-marketing-pipeline/src')

from config.settings import DatabaseConfig
from processors.silver_processor import SilverProcessor
from datetime import datetime
import logging

# COMMAND ----------

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize configuration
db_config = DatabaseConfig()

# Initialize processor
processor = SilverProcessor(spark, db_config)

# Process current hour
logger.info("Starting bronze to silver processing...")
processor.process_hour()
logger.info("Bronze to silver processing completed.")
