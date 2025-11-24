import json
from rich import print
from datetime import datetime

from services.shared.notification import Notification

from services.shared.simple_order import SimpleOrder


class NotificationProcessor:

    def __init__(self, id, status_callback):
        self.service_id = id
        self.orders = {}
        self.status_callback = status_callback

    def process_notification(self, body):
        order_json = json.loads(body)

        data = order_json.get("order", order_json)
        order_object = SimpleOrder(**data)

        notification = Notification.from_order_schema(order_object)

        self.print_status(notification)
        self.status_callback(notification)

        return notification

    def print_status(self, notification):
        print(
            f"[spring_green3][Notification {self.service_id}][/spring_green3] {datetime.now().strftime('%H:%M:%S')} - [Pedido {notification.order.id}] Notificação enviada"
        )
