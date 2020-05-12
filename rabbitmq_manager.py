import pika
import threading
from src.service import *


def init(connection):
    channel = connection.channel()

    # declare queues and exchange for orders
    for service_name in services_dic.values():
        channel.queue_declare(queue=service_name, durable=True)

    channel.exchange_declare(exchange='orders', exchange_type='topic')

    for service_name in services_dic.values():
        channel.queue_bind(exchange='orders', queue=service_name, routing_key=service_name)

    # declare exchange for messages
    channel.exchange_declare(exchange='messages', exchange_type='direct')

    # QoS
    channel.basic_qos(prefetch_count=1)

    return channel


# can be used instead of channel.start_consuming()
# allows to process messages in parallel with another tasks
# every  0.1 sec checks for new messages
def start_consuming(connection):
    consumer = threading.Timer(0.1, start_consuming, [connection])
    consumer.daemon = True
    consumer.start()

    connection.process_data_events()
