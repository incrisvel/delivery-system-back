import uuid
from datetime import datetime
import threading
from queue import Queue
from rich import print
from services.shared.components_enum import Exchanges, Queues
from services.shared.notification import Notification

from .processor import DeliveryProcessor
from services.shared.connection_manager import ConnectionManager, reconnect


class DeliveryService:
    MAX_RETRIES = 5

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
            Exchanges.DEAD_LETTER_EXCHANGE.declaration,
            Exchanges.DEAD_LETTER_EXCHANGE.type,
        )

        delivery_arguments = {
            "x-dead-letter-exchange": Exchanges.DEAD_LETTER_EXCHANGE.declaration,
            "x-dead-letter-routing-key": "delivery.retry",
        }

        self.delivery_queue = self.connection.create_queue(
            self.channel_consumer,
            Queues.DELIVERY_QUEUE,
            bindings=[
                {
                    "exchange": Exchanges.ORDER_EXCHANGE.declaration,
                    "routing_key": "order.created",
                },
                {
                    "exchange": Exchanges.DEAD_LETTER_EXCHANGE.declaration,
                    "routing_key": "delivery.process",
                },
            ],
            arguments=delivery_arguments,
        )

        retry_arguments = {
            "x-message-ttl": 15000,
            "x-dead-letter-exchange": Exchanges.DEAD_LETTER_EXCHANGE.declaration,
            "x-dead-letter-routing-key": "delivery.process",
        }

        self.connection.create_queue(
            self.channel_consumer,
            Queues.DELIVERY_RETRY_QUEUE,
            bindings=[
                {
                    "exchange": Exchanges.DEAD_LETTER_EXCHANGE.declaration,
                    "routing_key": "delivery.retry",
                }
            ],
            arguments=retry_arguments,
        )

        self.connection.create_queue(
            self.channel_consumer,
            Queues.DEAD_LETTER_QUEUE,
            bindings=[
                {
                    "exchange": Exchanges.DEAD_LETTER_EXCHANGE.declaration,
                    "routing_key": "delivery.dead",
                }
            ],
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

    def _handle_retry(self, ch, method, properties, body):
        headers = properties.headers or {}
        retry_count = headers.get("x-retry-count", 0)

        if retry_count >= self.MAX_RETRIES:
            print(
                f"[spring_green3][Delivery {self.id}][/spring_green3] "
                f"{datetime.now().strftime('%H:%M:%S')} Tentativas excedidas -> DLQ"
            )

            ch.basic_publish(
                exchange=Exchanges.DEAD_LETTER_EXCHANGE.declaration,
                routing_key="delivery.dead",
                body=body,
                properties=self.connection.define_publish_properties(
                    {"headers": {"x-retry-count": retry_count}}
                )
            )

            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        new_retry_count = retry_count + 1

        print(
            f"[spring_green3][Delivery {self.id}][/spring_green3] "
            f"{datetime.now().strftime('%H:%M:%S')} Enviando para retry ({new_retry_count}/{self.MAX_RETRIES})"
        )

        ch.basic_publish(
            exchange=Exchanges.DEAD_LETTER_EXCHANGE.declaration,
            routing_key="delivery.retry",
            body=body,
            properties=self.connection.define_publish_properties(
                {"headers": {"x-retry-count": new_retry_count}}
            )
        )

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def process_order_created(self, ch, method, properties, body):
        if properties.content_type != "application/json":
            print(
                f"[spring_green3][Delivery {self.id}][/spring_green3] "
                f"{datetime.now().strftime('%H:%M:%S')} Tipo de conteúdo inválido: {properties.content_type}"
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        try:
            self.processor.process_new_order(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            print(
                f"[spring_green3][Delivery {self.id}][/spring_green3] "
                f"{datetime.now().strftime('%H:%M:%S')} Erro no processamento: {e}"
            )
            self._handle_retry(ch, method, properties, body)

    def publish_order_update(self, order):
        notification = Notification.from_order_schema(order)
        key = f"order.delivery.{order.status.value}"
        self.publish_notification(key, notification)

    @reconnect
    def publish_notification(self, key, notification: Notification):
        payload = notification.model_dump_json()
        self.channel_producer.basic_publish(
            exchange=Exchanges.ORDER_EXCHANGE.declaration,
            routing_key=key,
            body=payload,
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

    @reconnect
    def consume(self):
        print(f"[spring_green3][Delivery {self.id}][/spring_green3] "
              f"{datetime.now().strftime('%H:%M:%S')} Aguardando atualizações...")
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
            print(f"[spring_green3][Delivery {self.id}][/spring_green3] "
                  f"{datetime.now().strftime('%H:%M:%S')} Pressione 'Ctrl + C' para sair.\n")

            while True:
                pass

        except KeyboardInterrupt:
            print(f"\n[spring_green3][Delivery {self.id}][/spring_green3] "
                  f"{datetime.now().strftime('%H:%M:%S')} Encerrando.")

        finally:
            if self.channel_consumer.is_open:
                self.channel_consumer.connection.add_callback_threadsafe(
                    lambda: self.channel_consumer.stop_consuming()
                )

            self.consumer_thread.join()

            if self.channel_consumer.connection.is_open:
                self.channel_consumer.close()

            print(f"[spring_green3][Delivery {self.id}][/spring_green3] "
                  f"{datetime.now().strftime('%H:%M:%S')} Conexão fechada.")


if __name__ == "__main__":
    svc = DeliveryService()
    svc.run()
