from datetime import datetime, timezone
import json

from .simple_order import SimpleOrder, OrderStatus


class Processor:
    def __init__(self, id, status_callback):
        self.service_id = id
        self.orders = {}
        self.status_callback = status_callback

    def process_new_order(self, body):
        order_json = json.loads(body)
        print(body)
        order_object = SimpleOrder(**order_json)

        if self.orders.get(order_object.order) is not None:
            print(f"[Delivery {self.service_id}] Pedido {order_object.order} já foi processado.")
            return

        order = self.generate_delivery_id(order_object)
        self.status_callback(order)

        order = self.assign_courier(order)
        self.status_callback(order)

        order = self.calculate_estimated_arrival(order)
        self.status_callback(order)

        self.orders[order.order] = order

        self.print_status(order)

        return order

    def generate_delivery_id(self, order):
        order.generate_delivery_id()
        order.change_status(OrderStatus.ATUALIZADO)

        return order

    def assign_courier(self, order):
        order.assign_random_courier()
        order.change_status(OrderStatus.ATRIBUÍDO)

        return order

    def calculate_estimated_arrival(self, order):
        order.calculate_estimated_arrival()
        order.change_status(OrderStatus.EM_ENTREGA)

        return order

    def print_status(self, order):
        print(f"[Delivery {self.service_id}] {order.courier} saiu para a entrega do pedido {order.order}.")
        print(f"[Delivery {self.service_id}] O pedido {order.order} chegará às {order.estimated_arrival_at}.")

    def check_delivered_orders(self):
        for order in list(self.orders.values()):
                if order.status == OrderStatus.EM_ENTREGA and order.estimated_arrival_at is not None:
                    if datetime.now(timezone.utc) >= order.estimated_arrival_at:
                        order.change_status(OrderStatus.ENTREGUE)

                        print(f"[Delivery {self.service_id}] O pedido {order.order} foi entregue por {order.courier}.")
                        self.status_callback(order)

                        self.orders.pop(order.order, None)
