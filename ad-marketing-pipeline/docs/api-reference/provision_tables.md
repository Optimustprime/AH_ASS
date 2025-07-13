# Provision Tables

This notebook sets up the initial database structure including catalog, schemas, and tables.

# Databricks notebook source
import sys
sys.path.append('/Workspace/path/to/your/project/src')

from config.settings import DatabaseConfig
from utils.database_manager import DatabaseManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize configuration
db_config = DatabaseConfig()

# Initialize database manager
db_manager = DatabaseManager(spark, db_config)

# Create catalog and schemas
logger.info("Creating catalog and schemas...")
db_manager.create_catalog_and_schemas()

# Create tables
logger.info("Creating tables...")
db_manager.create_tables()

logger.info("Database provisioning completed successfully!")