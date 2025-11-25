import pika
from rich import print
from pika import exceptions
from typing import Dict, Any

from .settings import settings


class ConnectionManager:
    def __init__(self):
        credentials = pika.PlainCredentials(
            settings.rabbitmq_user, settings.rabbitmq_pass
        )

        self.parameters = pika.ConnectionParameters(
            host=settings.rabbitmq_host,
            port=settings.rabbitmq_port,
            virtual_host=settings.rabbitmq_vhost,
            credentials=credentials,
            heartbeat=60,
            blocked_connection_timeout=60,
        )

    def create_connection(self):
        return pika.BlockingConnection(self.parameters)

    def create_channel(self):
        conn = self.create_connection()
        return conn.channel()

    def create_exchange(self, channel, name, type):
        return channel.exchange_declare(exchange=name, exchange_type=type, durable=True)

    def create_queue(self, channel, queue_name, bindings=None, arguments=None):
        queue = channel.queue_declare(
            queue=queue_name, durable=True, arguments=arguments
        ).method.queue

        if bindings:
            for binding in bindings:
                channel.queue_bind(
                    exchange=binding["exchange"],
                    queue=queue_name,
                    routing_key=binding.get("routing_key", ""),
                )

        return queue

    def define_publish_properties(self, properties: Dict[str, Any]):
        props = properties.copy()

        content_type = props.pop("content_type", "application/json")
        delivery_mode = props.pop("delivery_mode", pika.DeliveryMode.Persistent)

        return pika.BasicProperties(
            content_type=content_type, delivery_mode=delivery_mode, **props
        )


def reconnect(method):
    def wrapper(self, *args, **kwargs):
        try:
            return method(self, *args, **kwargs)
        except exceptions.AMQPError as e:
            print(f"[light_goldenrod1]WARN:[/light_goldenrod1] Conexão perdida durante {method.__name__}: {e}")
            print("[light_goldenrod1]WARN:[/light_goldenrod1] Criando nova conexão e canal...")

            new_channel = self.connection.create_channel()

            if "consumer" in method.__name__:
                self.channel_consumer = new_channel
            else:
                self.channel_producer = new_channel

            return method(self, *args, **kwargs)

    return wrapper
