import pika
import uuid

from ..settings import settings

class DeliveryService:
    def __init__(self):
        self.id = str(uuid.uuid4())[:4]
        self.deliveries = {}

        credentials = pika.PlainCredentials(
            settings.rabbitmq_user,
            settings.rabbitmq_pass
        )

        parameters = pika.ConnectionParameters(
            settings.rabbitmq_host,
            settings.rabbitmq_port,
            settings.rabbitmq_vhost,
            credentials
        )

if __name__ == "__main__":
    service = DeliveryService()
    print(f"Delivery Service - ID: {service.id}")
