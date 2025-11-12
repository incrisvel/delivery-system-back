import pika
import uuid

from services.service_utils import service_manager

from ..settings import settings


class NotificationService:
    def __init__(self):
        self.id = str(uuid.uuid4())[:4]
        self.deliveries = {}

        credentials = pika.PlainCredentials(
            settings.rabbitmq_user, settings.rabbitmq_pass
        )

        parameters = pika.ConnectionParameters(
            settings.rabbitmq_host,
            settings.rabbitmq_port,
            settings.rabbitmq_vhost,
            credentials,
        )

        self.service_manager = service_manager.ServiceManager(settings)

        self.__components_setup()

    def __components_setup(self):

        self.__consumer_setup()
        self.__producer_setup()

    def __consumer_setup(self):
        self.channel_consumer = self.service_manager.create_channel()
        self.orders_exchange = self.service_manager.create_exchange(
            self.channel_consumer, "orders_exchange", "topic"
        )
        self.notification_queue = self.service_manager.create_queue(
            self.channel_consumer,
            "notification_queue",
            bindings=[
                {"exchange": "orders_exchange", "routing_key": "order.*"}
            ]
        )

    def __producer_setup(self):
        self.channel_producer = self.service_manager.create_channel()
        self.notifications_exchange = self.service_manager.create_exchange(
            self.channel_producer, "notifications_exchange", "fanout"
        )
        self.orders_queue = self.service_manager.create_queue(
            self.channel_producer,
            "orders_queue",
            bindings=[
                {"exchange": "notifications_exchange"},
            ]
        )
        self.delivery_queue = self.service_manager.create_queue(
            self.channel_producer,
            "delivery_queue",
            bindings=[
                {"exchange": "notifications_exchange"},
            ]
        )

if __name__ == "__main__":
    service = NotificationService()
    print(f"Notification Service - ID: {service.id}")
