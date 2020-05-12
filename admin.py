import pika
from src.service import *
import src.rabbitmq_manager as rabbitmq_manager

receiver_dic = {'a': 'agent', 'c': 'carrier', '-': 'to_all'}


# sends message to receivers
def call(receiver):
    global channel
    channel.basic_publish(
        exchange='messages',
        routing_key=receiver_dic.get(receiver),
        properties=pika.BasicProperties(
            correlation_id='0',
            app_id='admin',),
        body='MESSAGE FROM ADMIN')


# prints all messages
def callback(ch, method, props, body):
    print("> APP_ID: " + str(props.app_id) + "      CORRELATION_ID: " + str(props.correlation_id) + "      BODY: " + body.decode('utf-8'))


# RabbitMQ connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = rabbitmq_manager.init(connection)

# unique queue for admin
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

# receive all messages from exchanges
channel.queue_bind(exchange='orders', queue=queue_name, routing_key='#')

channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
rabbitmq_manager.start_consuming(connection)

print("""You can stop admin by writing 'stop' or send message writing:
    a - send message to all agencies
    c - send message to all carriers 
    - - send message to everybody
""")

try:
    while True:
        service = input()
        if service == 'stop':
            break
        else:
            call(service)
finally:
    connection.close()

