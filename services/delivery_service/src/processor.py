import json
import random
import time

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from services.shared.simple_order import SimpleOrder, OrderStatus


class DeliveryProcessor:
    MIN_PROCESSING_TIME = 0.5
    MAX_PROCESSING_TIME = 5.0

    def __init__(self, id, status_callback):
        self.service_id = id
        self.orders = {}
        self.status_callback = status_callback

    def process_new_order(self, body):
        order_json = json.loads(body)
        order_object = SimpleOrder(**order_json["order"])

        time.sleep(random.uniform(self.MIN_PROCESSING_TIME, self.MAX_PROCESSING_TIME))

        if self.orders.get(order_object.id) is not None:
            # print(
            #     f"[Delivery {self.service_id}] Pedido {order_object.id} já foi processado."
            # )
            return

        order = self.generate_delivery_id(order_object)
        self.status_callback(order)

        time.sleep(5)

        order = self.assign_courier(order)
        self.status_callback(order)

        time.sleep(5)

        order = self.calculate_estimated_arrival(order)
        self.status_callback(order)

        time.sleep(5)

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
        local_sent_time = order.updated_at.astimezone(ZoneInfo("America/Sao_Paulo"))
        print(
            f"[Delivery {self.service_id}] {order.courier} saiu para a entrega do pedido {order.id} às {local_sent_time:%H:%M:%S} UTC-3."
        )

        local_arrival_time = order.estimated_arrival_at.astimezone(
            ZoneInfo("America/Sao_Paulo")
        )
        print(
            f"[Delivery {self.service_id}] O pedido {order.id} chegará às {local_arrival_time:%H:%M:%S} UTC-3."
        )

    def check_delivered_orders(self):
        for order in list(self.orders.values()):
            if (
                order.status != OrderStatus.ENROUTE
                or order.estimated_arrival_at is None
            ):
                continue

            if datetime.now(timezone.utc) >= order.estimated_arrival_at:
                order.change_status(OrderStatus.DELIVERED)

                print(
                    f"[Delivery {self.service_id}] O pedido {order.id} foi entregue por {order.courier}."
                )
                self.status_callback(order)

                self.orders.pop(order.id, None)
