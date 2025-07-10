from kafka import KafkaProducer
import json
import logging
from datetime import datetime
import uuid
import os
from azure.eventhub import EventHubProducerClient, EventData
from azure.eventhub.exceptions import EventHubError

logger = logging.getLogger(__name__)

class AzureKafkaClickProducer:
    def __init__(self):
        # Get connection string from environment variable
        self.connection_string = os.environ.get('KAFKA_CONNECTION_STRING')
        self.eventhub_name = os.environ.get('KAFKA_TOPIC', 'ad_clicks')
        self.producer = None

        if self.connection_string:
            try:
                self.producer = EventHubProducerClient.from_connection_string(
                    conn_str=self.connection_string,
                    eventhub_name=self.eventhub_name
                )
                logger.info("Azure Event Hub producer initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Azure Event Hub producer: {e}")

    def send_click_event(self, advertiser_id: int, ad_id: str, amount: float, budget_value: float):
        """Send ad click event to Azure Event Hub."""
        if not self.producer:
            logger.error("Event Hub producer not initialized")
            return False

        click_event = {
            "event_type": "ad_click",
            "click_id": f"c{uuid.uuid4().hex[:6]}",
            "advertiser_id": str(advertiser_id),
            "ad_id": ad_id,
            "amount": amount,
            "budget_value": budget_value,
            "timestamp": datetime.utcnow().isoformat(),
        }

        try:
            event_data_batch = self.producer.create_batch()
            event_data_batch.add(EventData(json.dumps(click_event).encode('utf-8')))

            self.producer.send_batch(event_data_batch)
            logger.info(f"Click event sent to Azure Event Hub: {click_event}")
            return True
        except EventHubError as e:
            logger.error(f"Failed to send click event to Azure Event Hub: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when sending click event: {e}")
            return False

    def close(self):
        if self.producer:
            self.producer.close()