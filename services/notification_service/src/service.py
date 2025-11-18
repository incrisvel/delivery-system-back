import uuid

from ...service_utils.connection_manager import ConnectionManager


class NotificationService:
    def __init__(self):
        self.id = str(uuid.uuid4())[:4]
        self.deliveries = {}

        self.connection = ConnectionManager()

        self.__components_setup()

    def __components_setup(self):

        self.__consumer_setup()
        self.__producer_setup()

    def __consumer_setup(self):
        self.channel_consumer = self.connection.create_channel()
        self.orders_exchange = self.connection.create_exchange(
            self.channel_consumer, "orders_exchange", "topic"
        )
        self.notification_queue = self.connection.create_queue(
            self.channel_consumer,
            "notification_queue",
            bindings=[
                {"exchange": "orders_exchange", "routing_key": "order.*"}
            ]
        )

    def __producer_setup(self):
        self.channel_producer = self.connection.create_channel()
        self.notifications_exchange = self.connection.create_exchange(
            self.channel_producer, "notifications_exchange", "fanout"
        )
        self.orders_queue = self.connection.create_queue(
            self.channel_producer,
            "orders_queue",
            bindings=[
                {"exchange": "notifications_exchange"},
            ]
        )
        self.delivery_queue = self.connection.create_queue(
            self.channel_producer,
            "delivery_queue",
            bindings=[
                {"exchange": "notifications_exchange"},
            ]
        )

if __name__ == "__main__":
    service = NotificationService()
    print(f"Notification Service - ID: {service.id}")
