import pika
from typing import Dict, Any

from .settings import settings

class ConnectionManager:

    def __init__(self):
        credentials = pika.PlainCredentials(
            settings.rabbitmq_user, settings.rabbitmq_pass
        )

        self.parameters = pika.ConnectionParameters(
            settings.rabbitmq_host,
            settings.rabbitmq_port,
            settings.rabbitmq_vhost,
            credentials,
        )

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

    def create_queue(self, channel, queue_name, bindings: Dict[str, Any] = None, arguments: Dict[str, Any] = None):
        queue = channel.queue_declare(queue=queue_name, durable=True, arguments=arguments).method.queue
        if bindings:
            for binding in bindings:
                exchange = binding.get("exchange")
                if not exchange:
                    continue
                routing_key = binding.get("routing_key", None)
                if routing_key is None:
                    channel.queue_bind(exchange=exchange, queue=queue_name)
                else:
                    channel.queue_bind(exchange=exchange, queue=queue_name, routing_key=routing_key)
        return queue

    def define_publish_properties(self, properties: Dict[str, Any]):
        props = properties.copy()

        content_type = props.pop("content_type", "application/json")
        delivery_mode = props.pop("delivery_mode", pika.DeliveryMode.Persistent)

        return pika.BasicProperties(
            content_type=content_type,
            delivery_mode=delivery_mode,
            **props
        )
