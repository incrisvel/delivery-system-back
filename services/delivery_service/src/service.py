import json
import uuid
import threading

from .processor import Processor
from .simple_order import SimpleOrder
from ...shared.connection_manager import ConnectionManager


class DeliveryService:
    def __init__(self):
        self.id = str(uuid.uuid4())[:4]

        self.processor = Processor(id)
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
                                            on_message_callback=self.processor.process_order_created,
                                            auto_ack=False)

    def __producer_setup(self):
        self.channel_producer = self.connection.create_channel()
        self.order_exchange = self.connection.create_exchange(
            self.channel_producer, "order_exchange", "topic"
        )

    def publish(self, key, body):
        self.channel_producer.basic_publish(
            exchange="order_exchange",
            routing_key=key,
            body=body.model_dump_json(),
            properties=self.connection.define_publish_properties({
                "headers": {"service_id": self.id}
            })
        )

    def listen(self):
        print(f"[Delivery {self.id}] Aguardando atualizações...")
        self.channel_consumer.start_consuming()

    def run(self):
        consumer_thread = threading.Thread(target=self.listen, daemon=True)
        consumer_thread.start()

        try:
            print(f"[Delivery {self.id}] Pressione 'Ctrl + C' para sair.\n")

            while True:
                user_input = input()

                if user_input.lower() == 'p': # Teste manual

                    self.publish(
                        key="order.created",
                        body=SimpleOrder.create_random()
                    )

        except KeyboardInterrupt:
            print(f"\n[Delivery {self.id}] Encerrando.")

        finally:
            if self.channel_consumer.is_open:
                self.channel_consumer.connection.add_callback_threadsafe(
                    lambda: self.channel_consumer.stop_consuming()
                )

            consumer_thread.join()

            if self.channel_consumer.connection.is_open:
                self.channel_consumer.close()

            print(f"[Delivery {self.id}] Conexão fechada.")

if __name__ == '__main__':
    svc = DeliveryService()
    svc.run()
