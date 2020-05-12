import pika
import uuid
import threading
import src.rabbitmq_manager as rabbitmq_manager
from src.service import *


# sends request for a service
def send_request(service):
    global order_id, callback_queue, agency_id
    if service not in services_dic.keys():
        print("Service not found")
        return
    order_id += 1
    channel.basic_publish(
        exchange='orders',
        routing_key=services_dic.get(service),
        properties=pika.BasicProperties(
            reply_to=callback_exchange,
            correlation_id=str(order_id),
            app_id=str(agency_id),),
        body='')


# handles return messages
def handle_message(ch, method, props, body):
    if props.app_id == 'admin':
        print("From admin: " + body.decode('utf-8'))
    else:
        print("Order " + props.correlation_id + ": " + body.decode('utf-8'))


# unique agency id and incremented order id
agency_id = uuid.uuid4()
order_id = 0

# RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = rabbitmq_manager.init(connection)

# unique queue for agent
result = channel.queue_declare(queue='')
callback_queue = result.method.queue

callback_exchange = 'agent.' + str(agency_id)
channel.queue_bind(exchange='orders', queue=callback_queue, routing_key=callback_exchange)
channel.queue_bind(exchange='messages', queue=callback_queue, routing_key='agent')
channel.queue_bind(exchange='messages', queue=callback_queue, routing_key='to_all')

# receiving messages
channel.basic_consume(queue=callback_queue, on_message_callback=handle_message, auto_ack=True)
rabbitmq_manager.start_consuming(connection)

# sending messages
print("Select required service: \n" + list_services())
try:
    while True:
        i = input()
        if i == 'stop':
            break
        else:
            send_request(i)
finally:
    connection.close()
