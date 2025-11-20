

class Processor:
    def __init__(self, id):
        self.service_id = id

    def process_order_created(self, ch, method, properties, body):
        print(f"[Delivery {self.service_id}] Chegou aqui")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def assign_courier(self, order_id):
        print(f"[Delivery {self.service_id}] Atribuindo entregador para o pedido {order_id}")
