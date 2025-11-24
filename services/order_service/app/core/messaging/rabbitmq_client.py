from queue import Queue
import threading
import uuid
import json

from services.order_service.app.core.utils.models import update_model_from_schema
from services.order_service.app.core.db.session import get_session
from services.shared.simple_order import OrderStatus
from services.order_service.app.modules.order.repository import OrderRepository
from services.order_service.app.modules.delivery.repository import DeliveryRepository
from services.shared.components_enum import Exchanges, Queues
from services.shared.connection_manager import ConnectionManager
from services.shared.notification import Notification


class RabbitMQClient:
    def __init__(self):
        self.id = str(uuid.uuid4())[:4]
        self.producer_queue = Queue()
        self.connection = ConnectionManager()
        self.running = False

        self._components_setup()

    def _components_setup(self):
        self._consumer_setup()
        self._producer_setup()

    def _consumer_setup(self):
        self.channel_consumer = self.connection.create_channel()
        self.connection.create_exchange(
            self.channel_consumer,
            Exchanges.NOTIFICATION_EXCHANGE.declaration,
            Exchanges.NOTIFICATION_EXCHANGE.type,
        )

        self.connection.create_queue(
            self.channel_consumer,
            Queues.ORDER_QUEUE,
            bindings=[
                {
                    "exchange": Exchanges.NOTIFICATION_EXCHANGE.declaration,
                    "routing_key": "",
                }
            ],
        )

        self.channel_consumer.basic_consume(
            queue=Queues.ORDER_QUEUE,
            on_message_callback=self.process_notification,
            auto_ack=False,
        )

    def _producer_setup(self):
        self.channel_producer = self.connection.create_channel()
        self.notification_exchange = self.connection.create_exchange(
            self.channel_producer,
            Exchanges.ORDER_EXCHANGE.declaration,
            Exchanges.ORDER_EXCHANGE.type,
        )

    def process_notification(
        self,
        ch,
        method,
        properties,
        body,
    ):
        session = next(get_session())
        try:
            if properties.content_type != "application/json":
                print(f"[Order {self.id}] Tipo inválido: {properties.content_type}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            notification = Notification(**json.loads(body))

            print(f"[Order {self.id}] Recebido:", notification)

            if notification.order.status == OrderStatus.ASSIGNED:
                self._assign_delivery_courier(notification.order, session)

            self._update_order_status(notification.order, session)
        except Exception as e:
            print(f"[Order {self.id}] ERRO:", e)

        finally:
            ch.basic_ack(delivery_tag=method.delivery_tag)

    def _update_order_status(self, simple_order, session):
        repo = OrderRepository(session=session)
        order = repo.get_order_by_id(simple_order.id)
        update_model_from_schema(order, simple_order)
        repo.update_order(order)
        repo.session.commit()

    def _assign_delivery_courier(self, order, session):
        delivery_repo = DeliveryRepository(session=session)
        delivery = delivery_repo.get_delivery_by_id(order.delivery_id)
        delivery.courier = order.courier
        delivery_repo.session.flush()


    def publish_delivery_status_changed(self, order):
        notification = Notification.from_order_schema(order)
        key = f"order.delivery.{order.status.value}"
        self.publish_notification(key, notification)

    def publish_order_status_changed(self, order):
        notification = Notification.from_order_schema(order=order)
        key = f"order.{order.status.value}"
        self.publish_notification(key, notification)

    def publish_notification(self, key: str, notification: Notification):
        payload = notification.model_dump_json()
        self.channel_producer.basic_publish(
            exchange=Exchanges.ORDER_EXCHANGE.declaration,
            routing_key=key,
            body=payload,
            properties=self.connection.define_publish_properties(
                {"headers": {"service_id": self.id}}
            ),
        )
        print(f"[Order {self.id}] Notificação enviada:", payload)

    def produce(self):
        while self.running:
            try:
                notification = self.producer_queue.get(timeout=0.5)
                self.publish_notification(notification)
                self.producer_queue.task_done()
            except Exception:
                pass

    def consume(self):
        print(f"[Order {self.id}] Aguardando notificações...")
        try:
            self.channel_consumer.start_consuming()
        except Exception as e:
            print("Erro no consumidor:", e)

    def run(self):
        self.running = True

        self.consumer_thread = threading.Thread(target=self.consume, daemon=True)
        self.consumer_thread.start()

        self.producer_thread = threading.Thread(target=self.produce, daemon=True)
        self.producer_thread.start()

    def stop(self):
        self.running = False
        if self.channel_consumer.is_open:
            self.channel_consumer.stop_consuming()

        self.consumer_thread.join(timeout=3)
        self.producer_thread.join(timeout=3)

        self.channel_consumer.close()
        self.channel_producer.close()

        print(f"[Order {self.id}] Conexões encerradas.")
