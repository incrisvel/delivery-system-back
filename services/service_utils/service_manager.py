import pika
import uuid
from typing import Dict, Any

parameters = None

class ServiceManager:

    def __init__(self, parameters):
        self.parameters = parameters

    def create_channel(self):
        connection = pika.BlockingConnection(self.parameters)
        channel = connection.channel()
        return channel

    def create_exchange(self, channel, exchange_name, exchange_type):
        exchange = channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=True
        )
        return exchange

    def create_queue(self, channel, queue_name, bindings: Dict[str, Any] = None):
        queue = channel.queue_declare(queue=queue_name, durable=True).method.queue
        if bindings:
            for binding in bindings:
                exchange = binding.get("exchange")
                if exchange:
                    routing_key = binding.get("routing_key")
                    channel.queue_bind(
                    exchange=exchange,
                    queue=queue_name,
                    routing_key=routing_key
                    )
        return queue

