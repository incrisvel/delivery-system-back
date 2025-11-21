
import json
import random
import time

from services.shared.notification import Notification

from ...shared.simple_order import SimpleOrder, OrderStatus


class NotificationProcessor:
    MIN_PROCESSING_TIME = 0.5
    MAX_PROCESSING_TIME = 5.0

    def __init__(self, id, status_callback):
        self.service_id = id
        self.orders = {}
        self.status_callback = status_callback

    def process_notification(self, body):
        order_json = json.loads(body)
        order_object = SimpleOrder(**order_json)

        time.sleep(random.uniform(self.MIN_PROCESSING_TIME, self.MAX_PROCESSING_TIME))

        notification = Notification(order_object)

        self.print_status(notification)

        return notification

    def print_status(self, notification):
        print(f"[Notification {self.service_id}] enviada às {notification.notification_time}.")
