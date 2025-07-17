# Broker MOM

import pika
import requests


# RabbitMQ Management API endpoint
BASE_URL = "http://localhost:15672/api"

# Manage AMQP queues and exchanges
class Broker:
    def __init__(self, host='127.0.0.1', port=5672):
        self.users = {} # Stores registered users (queues)
        self.topics = set() # Stores registered topics (fanout exchanges)

        # Establish AMQP connection to RabbitMQ
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host, port=port))

        # Establish AMQP channel to declare queues and exchanges.
        self.channel = self.connection.channel()

        # Recovers users and topics from RabbitMQ Management API
        self.sync_amqp()
    
    # Closes AMQP connection properly
    def close_connection(self):
        self.connection.close()

    # Synchronizes existing queues (users) and exchanges (topics) from RabbitMQ API
    def sync_amqp(self, auth=('guest', 'guest')):
        queues = requests.get(f"{BASE_URL}/queues", auth=auth).json()
        exchanges = requests.get(f"{BASE_URL}/exchanges", auth=auth).json()

        self.users = {queue["name"]: [] for queue in queues}
        self.topics = {exchange["name"] for exchange in exchanges if exchange["type"] == "fanout" and exchange["name"]}


    # # --------- Queue / Exchange Management Section ---------
    # Creates a queue for the user (direct communication)
    def create_user(self, username):
        self.channel.queue_declare(queue=username)

        # Register user to broker
        self.users[username] = []

    # Creates fanout exchange for broadcast messages
    def create_topic(self, topic):
        self.channel.exchange_declare(exchange=topic, exchange_type='fanout')

        # Register exchange to broker
        self.topics.add(topic)

    # Deletes exchange from broker
    def delete_topic(self, topic):
        self.channel.exchange_delete(exchange=topic)

        # Remove user from broker
        self.topics.remove(topic)