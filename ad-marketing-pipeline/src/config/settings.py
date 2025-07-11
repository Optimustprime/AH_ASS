# src/config/settings.py
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class DatabaseConfig:
    """Unity Catalog configuration for the ad marketing pipeline."""
    catalog: str = "ad_marketing_catalog"
    bronze_schema: str = "bronze"
    silver_schema: str = "silver"
    gold_schema: str = "gold"

    @property
    def bronze_table(self) -> str:
        return f"{self.catalog}.{self.bronze_schema}.ad_click_events_raw"

    @property
    def silver_table(self) -> str:
        return f"{self.catalog}.{self.silver_schema}.ad_click_events_clean"

    @property
    def gold_table(self) -> str:
        return f"{self.catalog}.{self.gold_schema}.advertiser_spend"

@dataclass
class EventHubConfig:
    """Event Hub configuration for streaming data."""
    connection_string_key: str = "EVENT_HUB_CONNECTION_STRING"
    scope: str = "ahass-scope"
    event_hub_name: str = "ad-clicks"
    checkpoint_location: str = "/delta/checkpoints/ad_click_events_raw"