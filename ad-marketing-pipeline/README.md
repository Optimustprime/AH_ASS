

# Ad Marketing Pipeline

A real-time data pipeline for ad marketing budget management using Apache Spark, Delta Lake, and Azure Event Hubs on Databricks.

## Overview

This pipeline processes ad click events in real-time to track advertiser spending against budgets and make serving decisions. It follows the medallion architecture pattern with Bronze, Silver, and Gold layers.

### Architecture
Event Hub → Bronze (Raw) → Silver (Clean) → Gold (Aggregated)

- **Bronze Layer**: Raw ad click events from Event Hub
- **Silver Layer**: Cleaned and validated events with data quality checks
- **Gold Layer**: Aggregated spend data by advertiser for budget decisions

## Features

- 🔄 Real-time streaming from Azure Event Hubs
- 📊 Medallion architecture for data quality
- 💰 Budget tracking and serving decisions
- 🏗️ Modular, type-safe Python code
- 📦 Poetry-based dependency management
- 🧪 Comprehensive testing framework
- 📝 Full documentation and type hints

## Project Structure

ad-marketing-pipeline/
├── pyproject.toml
├── README.md
├── src/
│   └───
│       ├── __init__.py
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── schemas.py
│       ├── processors/
│       │   ├── __init__.py
│       │   ├── bronze_processor.py
│       │   ├── silver_processor.py
│       │   └── gold_processor.py
│       ├── streaming/
│       │   ├── __init__.py
│       │   └── event_hub_streamer.py
│       └── utils/
│           ├── __init__.py
│           └── database_manager.py
├── notebooks/
│   ├── orchestration/
│   │   ├── run_bronze_to_silver.py
│   │   ├── run_silver_to_gold.py
│   │   └── setup_streaming.py
│   └── setup/
│       └── provision_tables.py
└── tests/
├── __init__.py
└── test_processors.py

## Quick Start

### Prerequisites

- Python 3.9+
- Poetry
- Databricks workspace
- Azure Event Hubs

### Installation

# Clone the repository
git clone https://github.com/your-org/ad-marketing-pipeline.git
cd ad-marketing-pipeline

# Install dependencies
poetry install

# Build the package
poetry build

Setup on Databricks
Upload the package to your Databricks workspace:  
# Upload src/ad_marketing_pipeline to /Workspace/your-path/
Configure secrets in Databricks:  
dbutils.secrets.put(scope="ahass-scope", key="EVENT_HUB_CONNECTION_STRING", value="your-connection-string")
Provision tables:  
# Run notebooks/setup/provision_tables.py
Running the Pipeline
Start streaming (Bronze layer):  
# Run notebooks/orchestration/setup_streaming.py
Process to Silver (scheduled hourly):  
# Run notebooks/orchestration/run_bronze_to_silver.py
Process to Gold (scheduled hourly):  
# Run notebooks/orchestration/run_silver_to_gold.py

Data Flow
Input Data Schema

{
  "event_type": "ad_click",
  "click_id": "unique-click-id",
  "advertiser": "advertiser-123",
  "ad_id": "ad-456",
  "amount": 0.50,
  "budget_value": 1000.0,
  "timestamp": "2024-01-01T12:00:00Z"
}

## Schema Diagram

```mermaid
classDiagram
direction LR
    class BronzeSchema {
        +StringType event_type
        +StringType click_id
        +StringType advertiser
        +StringType advertiser_id
        +StringType ad_id
        +FloatType amount
        +FloatType budget_value
        +TimestampType timestamp
    }
    
    class SilverSchema {
        +StringType event_type
        +StringType click_id
        +StringType advertiser
        +StringType advertiser_id
        +StringType ad_id
        +FloatType amount
        +FloatType budget_value
        +TimestampType timestamp
        +BooleanType is_valid
        +TimestampType processed_at
        +IntegerType ingest_year
        +IntegerType ingest_month
        +IntegerType ingest_day
        +IntegerType ingest_hour
    }
    
    class GoldSchema {
        +StringType advertiser
        +StringType advertiser_id
        +DoubleType gross_spend
        +DoubleType net_spend
        +LongType record_count
        +FloatType budget_value
        +BooleanType can_serve
        +TimestampType window_start
        +TimestampType window_end
        +TimestampType spend_hour
        +TimestampType spend_day
        +TimestampType spend_month
    }
    
    class CombinedSpendBudget {
        +String advertiser
        +Timestamp spend_day
        +String category
        +Float amount
    }

    class LatestChangedBudgets {
        +String advertiser
        +Timestamp spend_hour
        +Float budget_value
    }

    class LatestServingStatus {
        +String advertiser
        +Timestamp latest_hour
        +Boolean latest_can_serve
    }

    class HourlyAverageBudget {
        +String advertiser
        +Timestamp spend_hour
        +Float avg_budget
    }

    class AggregatedAdvertiserSpend {
        +String advertiser
        +Float total_gross_spend
        +Float total_net_spend
        +Long total_clicks
        +Float latest_budget_value
        +Timestamp latest_activity_time
        +Boolean current_serving_status
    }

    class MonthlySpend {
        +String advertiser
        +Timestamp spend_month
        +Float monthly_gross_spend
        +Float monthly_net_spend
        +Long total_clicks
        +Float budget_value
        +Boolean can_serve_status
    }

    class HourlySpend {
        +String advertiser
        +Timestamp spend_hour_start
        +Timestamp spend_hour_end
        +Float hourly_gross_spend
        +Float hourly_net_spend
    }

    class DailySpend {
        +String advertiser
        +Timestamp spend_day
        +Float daily_gross_spend
        +Float daily_net_spend
    }
    
    BronzeSchema --> SilverSchema: Cleaned & Validated
    SilverSchema --> GoldSchema: Aggregated by Advertiser
    GoldSchema <|-- CombinedSpendBudget
    GoldSchema <|-- LatestChangedBudgets
    GoldSchema <|-- LatestServingStatus
    GoldSchema <|-- HourlyAverageBudget
    GoldSchema <|-- AggregatedAdvertiserSpend
    GoldSchema <|-- MonthlySpend
    GoldSchema <|-- HourlySpend
    GoldSchema <|-- DailySpend