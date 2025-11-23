from enum import Enum


class Queues(str, Enum):
    DELIVERY_QUEUE = "delivery_queue"
    DELIVERY_RETRY_QUEUE = "delivery_retry_queue"
    NOTIFICATION_QUEUE = "notification_queue"
    ORDER_QUEUE = "order_queue"
    DEAD_LETTER_QUEUE = "dead_letter_queue"

class Exchanges(Enum):
    ORDER_EXCHANGE = ("order_exchange", "topic")
    NOTIFICATION_EXCHANGE = ("notification_exchange", "fanout")
    DEAD_LETTER_EXCHANGE = ("dead_letter_exchange", "direct")

    def __init__(self, declaration, type):
        self.declaration = declaration
        self.type = type
