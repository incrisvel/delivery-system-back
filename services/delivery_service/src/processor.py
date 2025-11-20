import json

from simple_order import SimpleOrder, OrderStatus


class Processor:
    def __init__(self, id):
        self.service_id = id
        self.orders = {}

    def process_new_order(self, body):
        order_json = json.loads(body)
        order_object = SimpleOrder(**order_json)

        if self.orders.get(order_object.order) is not None:
            print(f"[Delivery {self.service_id}] Pedido {order_object.order} já processado.")
            pass

        order = self.generate_delivery_id(order_object)
        order = self.assign_courier(order)
        order = self.calculate_estimated_arrival(order)

        self.orders[order.order] = order

        self.print_status(order)

        return order

    def generate_delivery_id(self, order):
        order.generate_delivery_id()
        order.change_status(OrderStatus.ATUALIZADO)

    def assign_courier(self, order):
        order.assign_random_courier()
        order.change_status(OrderStatus.ATRIBUÍDO)

    def calculate_estimated_arrival(self, order):
        order.calculate_estimated_arrival()
        order.change_status(OrderStatus.EM_ENTREGA)

    def print_status(self, order):
        print(f"[Delivery {self.service_id}] {order.courier} saiu para a entrega do pedido {order.order}.")
        print(f"[Delivery {self.service_id}] O pedido {order.order} chegará às {order.estimated_arrival_at}.")
