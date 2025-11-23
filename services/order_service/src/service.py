from queue import Queue
import threading
import uuid

from services.notification_service.src.processor import NotificationProcessor
from services.shared.components_enum import Exchanges, Queues
from services.shared.notification import Notification

from ...shared.connection_manager import ConnectionManager


class OrderService:
    def __init__(self):
        self.id = str(uuid.uuid4())[:4]
        self.producer_queue = Queue()

        #self.processor = OrderProcessor(self.id, self.on_status_change)
        self.connection = ConnectionManager()

        self.__components_setup()

    def __components_setup(self):
        self.__consumer_setup()
        self.__producer_setup()

    def __consumer_setup(self):

        self.channel_consumer = self.connection.create_channel()
        self.order_exchange = self.connection.create_exchange(
            self.channel_consumer, Exchanges.NOTIFICATION_EXCHANGE.declaration, Exchanges.NOTIFICATION_EXCHANGE.type
        )
        self.notification_queue = self.connection.create_queue(
            self.channel_consumer,
            Queues.ORDER_QUEUE,
            bindings=[
                {"exchange": Exchanges.NOTIFICATION_EXCHANGE.declaration}
            ]
        )

        # self.channel_consumer.basic_consume(queue=Queues.ORDER_QUEUE,
        #                                     on_message_callback=self.process_notification,
        #                                     auto_ack=False)

    def __producer_setup(self):
        self.channel_producer = self.connection.create_channel()
        self.notification_exchange = self.connection.create_exchange(
            self.channel_producer, Exchanges.ORDER_EXCHANGE.declaration, Exchanges.ORDER_EXCHANGE.type
        )

    def process_notification(self, ch, method, properties, body):
        # print(body)
        if properties.content_type != "application/json":
            print(f"[Notification {self.id}] Tipo de conteúdo inválido: {properties.content_type}")
            return

        #self.processor.process_notification(body)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    def publish_order(self):
        pass

    def on_status_change(self):
        pass

    def produce(self):
        while True:
            notification = self.producer_queue.get()
            if notification is None:
                break
        self.publish_notification(notification)
        self.producer_queue.task_done()

    def consume(self):
        print(f"[Order {self.id}] Aguardando notificações...")
        self.channel_consumer.start_consuming()

    def run(self):
        self.consumer_thread = threading.Thread(target=self.consume, daemon=True)
        self.consumer_thread.start()

        self.producer_thread = threading.Thread(target=self.produce, daemon=True)
        self.producer_thread.start()

        try:
            print(f"[Order {self.id}] Pressione 'Ctrl + C' para sair.\n")

            while True:
                pass

        except KeyboardInterrupt:
            print(f"\n[Order {self.id}] Encerrando.")

        finally:
            if self.channel_consumer.is_open:
                self.channel_consumer.connection.add_callback_threadsafe(
                    lambda: self.channel_consumer.stop_consuming()
                )

            self.consumer_thread.join()

            if self.channel_consumer.connection.is_open:
                self.channel_consumer.close()

            print(f"[Order {self.id}] Conexão fechada.")

if __name__ == '__main__':
    svc = OrderService()
    svc.run()
