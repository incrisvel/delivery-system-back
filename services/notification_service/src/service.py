from queue import Queue
import threading
import uuid

from services.notification_service.src.processor import NotificationProcessor
from services.shared.notification import Notification

from ...shared.connection_manager import ConnectionManager


class NotificationService:
    def __init__(self):
        self.id = str(uuid.uuid4())[:4]
        self.producer_queue = Queue()

        self.processor = NotificationProcessor(self.id, self.on_status_change)
        self.connection = ConnectionManager()

        self.__components_setup()

    def __components_setup(self):
        self.__consumer_setup()
        self.__producer_setup()

    def __consumer_setup(self):
        NOTIFCATION_QUEUE = "notification_queue"
        ORDER_EXCHANGE = "order_exchange"

        self.channel_consumer = self.connection.create_channel()
        self.order_exchange = self.connection.create_exchange(
            self.channel_consumer, ORDER_EXCHANGE, "topic"
        )
        self.notification_queue = self.connection.create_queue(
            self.channel_consumer,
            NOTIFCATION_QUEUE,
            bindings=[
                {"exchange": ORDER_EXCHANGE, "routing_key": "order.*"}
            ]
        )

        self.channel_consumer.basic_consume(queue=NOTIFCATION_QUEUE,
                                            on_message_callback=self.process_order_event,
                                            auto_ack=False)

    def __producer_setup(self):
        NOTIFICATION_EXCHANGE = "notification_exchange"

        self.channel_producer = self.connection.create_channel()
        self.notification_exchange = self.connection.create_exchange(
            self.channel_producer, NOTIFICATION_EXCHANGE, "fanout"
        )

    def process_order_event(self, ch, method, properties, body):
        if properties.content_type != "application/json":
            print(f"[Notification {self.id}] Tipo de conteúdo inválido: {properties.content_type}")
            return

        self.processor.process_notification(body)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def publish_notification(self, notification):
        self.channel_producer.basic_publish(
            exchange="notification_exchange",
            routing_key="",
            body=notification.model_dump_json(),
            properties=self.connection.create_message_properties(
                content_type="application/json",
                headers={"service_id": self.id}
            )
        )

    def on_status_change(self, notification):
        notification_copy = notification.model_copy(deep=True)
        self.producer_queue.put(notification_copy)

    def produce(self):
        while True:
            notification = self.producer_queue.get()
            if notification is None:
                break
        self.publish_notification(notification)
        self.producer_queue.task_done()

    def consume(self):
        print(f"[Notification {self.id}] Aguardando eventos de pedidos...")
        self.channel_consumer.start_consuming()

    def run(self):
        self.consumer_thread = threading.Thread(target=self.consume, daemon=True)
        self.consumer_thread.start()

        self.producer_thread = threading.Thread(target=self.produce, daemon=True)
        self.producer_thread.start()

        try:
            print(f"[Notification {self.id}] Pressione 'Ctrl + C' para sair.\n")

            while True:
                pass

        except KeyboardInterrupt:
            print(f"\n[Notification {self.id}] Encerrando.")

        finally:
            if self.channel_consumer.is_open:
                self.channel_consumer.connection.add_callback_threadsafe(
                    lambda: self.channel_consumer.stop_consuming()
                )

            self.consumer_thread.join()

            if self.channel_consumer.connection.is_open:
                self.channel_consumer.close()

            print(f"[Notification {self.id}] Conexão fechada.")

if __name__ == '__main__':
    svc = NotificationService()
    svc.run()
