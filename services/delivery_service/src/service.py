from random import randint
import uuid
import threading
from queue import Queue
from datetime import datetime, timezone

from .processor import DeliveryProcessor
from ...shared.simple_order import SimpleOrder, OrderStatus
from ...shared.connection_manager import ConnectionManager


class DeliveryService:
    def __init__(self):
        self.id = str(uuid.uuid4())[:4]
        self.producer_queue = Queue()

        self.processor = DeliveryProcessor(self.id, self.on_status_change)
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

        self.channel_consumer.basic_consume(queue="delivery_queue",
                                            on_message_callback=self.process_order_created,
                                            auto_ack=False)

    def __producer_setup(self):
        self.channel_producer = self.connection.create_channel()
        self.order_exchange = self.connection.create_exchange(
            self.channel_producer, "order_exchange", "topic"
        )

    def process_order_created(self, ch, method, properties, body):
        #print(body, properties)
        # if properties.headers.get("service_id") == self.id:
        #     return

        if properties.content_type != "application/json":
            print(f"[Delivery {self.id}] Tipo de conteúdo inválido: {properties.content_type}")
            return

        self.processor.process_new_order(body)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def publish_order_update(self, order):
        print(order)
        self.publish(
            key=f"order.{order.status.value}",
            body=order.model_dump_json()
            )

    def publish(self, key, body):
        self.channel_producer.basic_publish(
            exchange="order_exchange",
            routing_key=key,
            body=body,
            properties=self.connection.define_publish_properties({
                "headers": {"service_id": self.id}
            })
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

        self.time_thread = threading.Thread(target=self.check_delivery_time, daemon=True)
        self.time_thread.start()

        try:
            print(f"[Delivery {self.id}] Pressione 'Ctrl + C' para sair.\n")

            while True:
                user_input = input()

                if user_input.lower() == 'p': # Teste manual

                    self.publish(
                        key="order.created",
                        body=SimpleOrder(
                            order=randint(0, 9999),
                            created_at=datetime.now(timezone.utc),
                            updated_at=datetime.now(timezone.utc),
                            status=OrderStatus.CRIADO
                        ).to_json()
                    )

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

if __name__ == '__main__':
    svc = DeliveryService()
    svc.run()
