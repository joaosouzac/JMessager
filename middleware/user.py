import os
import json
import pika
import threading


# User
class User:
    def __init__(self, username, host='127.0.0.1', port=5672):
        self.username = username
        self.message_history = {self.username: []}
        self.subscriptions = set()
        self.amqp_host = host
        self.amqp_port = port


       # Directory and file for JSON persistence
        self._data_directory = os.path.join(
            os.path.dirname(
                os.path.dirname(__file__)
            ), "data"
        )

        os.makedirs(self._data_directory, exist_ok=True)

        self._history_path = os.path.join(
            self._data_directory, f"{self.username}_messages.json"
        )

        # Recover messages
        self.load_history()

        # Connection for direct messages
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host, port=port))

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=username)

        # Track topic connections to closer later
        self.topic_connections = []

        # Re-subscribe to previous topics
        for topic in self.subscriptions:
            self.subscribe_to_topic(topic, self.create_topic_callback(topic))



    # Save queues / exchanges history to file
    def save_history(self):
        data = {
            "subscriptions": list(self.subscriptions),
            "messages": self.message_history
        }

        with open(self._history_path, "w") as file:
            json.dump(data, file)

    # Load queues / exchanges history from file
    def load_history(self):
        if os.path.exists(self._history_path):
            with open(self._history_path, "r") as file:
                data = json.load(file)
                self.message_history.update(data.get("messages", {}))
                self.subscriptions = set(data.get("subscriptions", []))

    # Register queues / exchanges into the history
    def register_message(self, destination, message):
        if destination not in self.message_history:
            self.message_history[destination] = []

        self.message_history[destination].append(message)

        self.save_history()

    def quit_connection(self):
        self.save_history()
        self.connection.close()

        for conn in self.topic_connections:
            conn.close()

    # Listen to user's own queue
    def listen_user_queue(self, callback):
        self.channel.basic_consume(queue=self.username, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    # Function to send a direct message to another user
    def send_direct_message(self, destination, message):
        self.channel.basic_publish(exchange='', routing_key=destination, body=message)

    # Listen to a topic with dedicated connection and thread
    def subscribe_to_topic(self, topic, callback):
        if topic not in self.subscriptions:
            self.subscriptions.add(topic)
            self.save_history()

        connection = pika.BlockingConnection(pika.ConnectionParameters(self.amqp_host, port=self.amqp_port))
        channel = connection.channel()

        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue
        channel.queue_bind(exchange=topic, queue=queue_name)

        def consume():
            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            channel.start_consuming()

        thread = threading.Thread(target=consume, daemon=True)
        thread.start()

        self.topic_connections.append(connection)
    
    # Function to publish a message to a topic
    def publish_to_topic(self, topic, message):
        self.channel.basic_publish(exchange=topic, routing_key='', body=message)

    def create_topic_callback(self, topic):
        def callback(ch, method, properties, body):
            decoded = body.decode()
            self.register_message(topic, decoded)

        return callback