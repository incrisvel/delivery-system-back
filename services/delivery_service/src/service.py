import uuid
import threading
from queue import Queue

from services.shared.components_enum import Exchanges, Queues

from .processor import DeliveryProcessor
from services.shared.connection_manager import ConnectionManager


class DeliveryService:
    def __init__(self):
        self.id = str(uuid.uuid4())[:4]
        self.producer_queue = Queue()

        self.processor = DeliveryProcessor(self.id, self.on_status_change)
        self.connection = ConnectionManager()

        self._components_setup()

    def _components_setup(self):
        self._consumer_setup()
        self._producer_setup()

    def _consumer_setup(self):
        self.channel_consumer = self.connection.create_channel()
        self.connection.create_exchange(
            self.channel_consumer,
            Exchanges.ORDER_EXCHANGE.declaration,
            Exchanges.ORDER_EXCHANGE.type,
        )
        self.connection.create_exchange(
            self.channel_consumer,
            Exchanges.NOTIFICATION_EXCHANGE.declaration,
            Exchanges.NOTIFICATION_EXCHANGE.type,
        )

        self.delivery_queue = self.connection.create_queue(
            self.channel_consumer,
            Queues.DELIVERY_QUEUE,
            bindings=[
                {
                    "exchange": Exchanges.ORDER_EXCHANGE.declaration,
                    "routing_key": "order.created",
                },
                {
                    "exchange": Exchanges.NOTIFICATION_EXCHANGE.declaration,
                    "routing_key": ""},
            ]
        )

        self.connection.create_exchange(self.channel_consumer,
                                        Exchanges.DEAD_LETTER_EXCHANGE.declaration,
                                        Exchanges.DEAD_LETTER_EXCHANGE.type)

        retry_arguments = {
            'x-message-ttl': 15000,
            'x-dead-letter-exchange': Exchanges.ORDER_EXCHANGE.declaration,
        }

        self.connection.create_queue(
            self.channel_consumer,
            Queues.DELIVERY_RETRY_QUEUE,
            bindings=[
                {"exchange": Exchanges.ORDER_EXCHANGE.declaration, "routing_key": "delivery.retry"},
            ],
            arguments=retry_arguments
        )

        self.connection.create_queue(
            self.channel_consumer,
            Queues.DEAD_LETTER_QUEUE,
            bindings=[{"exchange": Exchanges.DEAD_LETTER_EXCHANGE.declaration}]
        )

        self.channel_consumer.basic_consume(
            queue=Queues.DELIVERY_QUEUE,
            on_message_callback=self.process_order_created,
            auto_ack=False,
        )

    def _producer_setup(self):
        self.channel_producer = self.connection.create_channel()
        self.order_exchange = self.connection.create_exchange(
            self.channel_producer,
            Exchanges.ORDER_EXCHANGE.declaration,
            Exchanges.ORDER_EXCHANGE.type,
        )

    def process_order_created(self, ch, method, properties, body):
        if properties.content_type != "application/json":
            print(
                f"[Delivery {self.id}] Tipo de conteúdo inválido: {properties.content_type}"
            )
            return

        self.processor.process_new_order(body)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def publish_order_update(self, order):
        self.publish(key=f"order.delivery.{order.status.value}", body=order.model_dump_json())

    def publish(self, key, body):
        self.channel_producer.basic_publish(
            exchange=Exchanges.ORDER_EXCHANGE.declaration,
            routing_key=key,
            body=body,
            properties=self.connection.define_publish_properties(
                {"headers": {"service_id": self.id}}
            ),
        )

    def on_status_change(self, order):
        order_copy = order.model_copy(deep=True)
        self.producer_queue.put(order_copy)

    def produce(self):
        while True:
            order = self.producer_queue.get()

            if order is None:
                break

            self.publish_order_update(order)
            self.producer_queue.task_done()

    def consume(self):
        print(f"[Delivery {self.id}] Aguardando atualizações...")
        self.channel_consumer.start_consuming()

    def check_delivery_time(self):
        while True:
            self.processor.check_delivered_orders()

            threading.Event().wait(30)

    def run(self):
        self.consumer_thread = threading.Thread(target=self.consume, daemon=True)
        self.consumer_thread.start()

        self.producer_thread = threading.Thread(target=self.produce, daemon=True)
        self.producer_thread.start()

        self.time_thread = threading.Thread(
            target=self.check_delivery_time, daemon=True
        )
        self.time_thread.start()

        try:
            print(f"[Delivery {self.id}] Pressione 'Ctrl + C' para sair.\n")

            while True:
                pass

        except KeyboardInterrupt:
            print(f"\n[Delivery {self.id}] Encerrando.")

        finally:
            if self.channel_consumer.is_open:
                self.channel_consumer.connection.add_callback_threadsafe(
                    lambda: self.channel_consumer.stop_consuming()
                )

            self.consumer_thread.join()

            if self.channel_consumer.connection.is_open:
                self.channel_consumer.close()

            print(f"[Delivery {self.id}] Conexão fechada.")


if __name__ == "__main__":
    svc = DeliveryService()
    svc.run()
