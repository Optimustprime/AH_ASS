from kafka import KafkaProducer
import json
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class KafkaClickProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['kafka:9091'],  # Match your docker-compose config
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=3,
            retry_backoff_ms=100
        )

    def send_click_event(self, advertiser: int, ad_id: str, amount: float = 1.20):
        """Send ad click event to Kafka."""
        click_event = {
            "event_type": "ad_click",
            "click_id": f"c{uuid.uuid4().hex[:6]}",
            "advertiser": str(advertiser),
            "ad_id": ad_id,
            "amount": amount,
            "timestamp": datetime.utcnow().isoformat(),
        }

        try:
            future = self.producer.send('ad_clicks', value=click_event)
            self.producer.flush()
            logger.info(f"Click event sent: {click_event}")
            return True
        except Exception as e:
            logger.error(f"Failed to send click event: {e}")
            return False

    def close(self):
        self.producer.close()