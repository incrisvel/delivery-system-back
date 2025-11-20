import uuid
import threading

from .processor import Processor
from ...shared.connection_manager import ConnectionManager


class DeliveryService:
    def __init__(self):
        self.id = str(uuid.uuid4())[:4]

        self.processor = Processor(id)
        self.connection = ConnectionManager()

        self.__components_setup()

    def __components_setup(self):
        self.__consumer_setup()
        self.__producer_setup()

    def __consumer_setup(self):
        self.channel_consumer = self.connection.create_channel()
        self.order_exchange = self.connection.create_exchange(
            self.channel_consumer, "order_exchange", "topic"
        )
        self.delivery_queue = self.connection.create_queue(
            self.channel_consumer,
            "delivery_queue",
            bindings=[
                {"exchange": "order_exchange", "routing_key": "order.created"}
            ]
        )

    def __producer_setup(self):
        self.channel_producer = self.connection.create_channel()
        self.order_exchange = self.connection.create_exchange(
            self.channel_producer, "order_exchange", "topic"
        )

    def listen(self):
        print(f"[Delivery {self.service_id}] Aguardando atualizações...")
        self.channel_consumer.start_consuming()

    def run(self):
        consumer_thread = threading.Thread(target=self.listen, daemon=True)
        consumer_thread.start()
        
        try:
            while True:
                user_input = input(f"[Delivery {self.service_id}] Pressione 'Ctrl + C' para sair.\n")
                
        except KeyboardInterrupt:
            print(f"\n[Delivery {self.service_id}] Encerrando.")
        
        finally:
            if self.channel_consumer.is_open:
                self.channel_consumer.connection.add_callback_threadsafe(
                    lambda: self.channel_consumer.stop_consuming()  
                )

            consumer_thread.join()
            
            if self.connection_consumer.is_open:
                self.connection_consumer.close()
                
            print(f"[Delivery {self.service_id}] Conexão fechada.")

if __name__ == '__main__':
    svc = DeliveryService()
    svc.run()