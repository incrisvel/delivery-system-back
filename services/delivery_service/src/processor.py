import json
import random
import time
from rich import print
from threading import Lock
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from services.shared.simple_order import SimpleOrder, OrderStatus


class DeliveryProcessor:
    MIN_PROCESSING_TIME = 0.5
    MAX_PROCESSING_TIME = 5.0

    def __init__(self, id, status_callback):
        self.service_id = id
        self.orders = {}
        self.orders_lock = Lock()
        self.status_callback = status_callback

    def process_new_order(self, body):
        order_json = json.loads(body)

        data = order_json.get("order", order_json)
        order = SimpleOrder(**data)

        time.sleep(random.uniform(self.MIN_PROCESSING_TIME, self.MAX_PROCESSING_TIME))

        with self.orders_lock:
            if order.id in self.orders:
                return

            self.orders[order.id] = None

        order = self.assign_courier(order)
        self.status_callback(order)

        time.sleep(5)

        order = self.calculate_estimated_arrival(order)
        self.status_callback(order)

        time.sleep(5)

        with self.orders_lock:
            self.orders[order.id] = order

        self.print_status(order)

        return order


    def generate_delivery_id(self, order):
        order.generate_delivery_id()
        order.change_status(OrderStatus.UPDATED)
        return order

    def assign_courier(self, order):
        order.assign_random_courier()
        order.change_status(OrderStatus.ASSIGNED)
        return order

    def calculate_estimated_arrival(self, order):
        order.calculate_estimated_arrival()
        order.change_status(OrderStatus.ENROUTE)
        return order

    def print_status(self, order):
        print(
            f"[spring_green3][Delivery {self.service_id}][/spring_green3] {datetime.now().strftime('%H:%M:%S')} - [Pedido {order.id}] {order.courier} saiu para a entrega do pedido"
        )

        local_arrival_time = order.estimated_arrival_at.astimezone(
            ZoneInfo("America/Sao_Paulo")
        )
        print(
            f"[spring_green3][Delivery {self.service_id}][/spring_green3] {datetime.now().strftime('%H:%M:%S')} - [Pedido {order.id}] Horário de entrega estimado: {local_arrival_time:%H:%M:%S}"
        )

    def check_delivered_orders(self):
        with self.orders_lock:
            orders_copy = list(self.orders.values())

        for order in orders_copy:
            if not order:
                continue

            if (
                order.status != OrderStatus.ENROUTE
                or order.estimated_arrival_at is None
            ):
                continue

            if datetime.now(timezone.utc) >= order.estimated_arrival_at:
                order.change_status(OrderStatus.DELIVERED)

                print(
                    f"[spring_green3][Delivery {self.service_id}][/spring_green3] {datetime.now().strftime('%H:%M:%S')} - [Pedido {order.id}] Pedido entregue"
                )
                self.status_callback(order)

                with self.orders_lock:
                    self.orders.pop(order.id, None)

