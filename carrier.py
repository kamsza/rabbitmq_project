import pika
from src.service import *
import src.rabbitmq_manager as rabbitmq_manager


# handles return messages
def handle_message(ch, method, props, body):
    print("Received: " + body.decode('utf-8'))


# welcome message with choice of supported services
print("Select two services provided by this carrier: \n" + list_services())
services = input("Enter services numbers:  ").split()

services[:] = [services_dic.get(e, '') for e in services]

# RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = rabbitmq_manager.init(connection)

# unique queue for carrier
result = channel.queue_declare(queue='')
callback_queue = result.method.queue
channel.queue_bind(exchange='messages', queue=callback_queue, routing_key='carrier')
channel.queue_bind(exchange='messages', queue=callback_queue, routing_key='to_all')


# handles requests from server
def on_request(ch, method, props, body, type_of_service):
    print("> FROM: " + str(props.app_id) + "      ORDER_ID: " + str(props.correlation_id) + "      FOR: " + type_of_service)

    ch.basic_publish(exchange='orders',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(
                         correlation_id=props.correlation_id,
                         app_id=str(props.app_id),),
                     body=type_of_service + " service completed")
    ch.basic_ack(delivery_tag=method.delivery_tag)


# receiving messages
for subscribed_queue in services:
    channel.basic_consume(queue=subscribed_queue,
                          on_message_callback=lambda ch, method, properties, body, type_of_service=subscribed_queue:
                              on_request(ch, method, properties, body, type_of_service))

channel.basic_consume(queue=callback_queue, on_message_callback=handle_message, auto_ack=True)
channel.start_consuming()
