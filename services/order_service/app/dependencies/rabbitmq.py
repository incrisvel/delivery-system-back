from services.order_service.app.core.messaging.rabbitmq_client import RabbitMQClient
from services.order_service.app.core.messaging import container

def get_rabbitmq_client() -> RabbitMQClient:
    return container.rabbitmq_client