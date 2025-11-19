import uuid

from ...shared.connection_manager import ConnectionManager


class DeliveryService:
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
        self.order_exchange = self.connection.create_exchange(
            self.channel_consumer, "order_exchange", "topic"
        )
        self.delivery_queue = self.connection.create_queue(
            self.channel_consumer,
            "delivery_queue",
            bindings=[
                {"exchange": "order_exchange", "routing_key": "order.created"}
            ]
        )

    def __producer_setup(self):
        self.channel_producer = self.connection.create_channel()
        self.order_exchange = self.connection.create_exchange(
            self.channel_producer, "order_exchange", "topic"
        )
