import pika
import threading

class User:
    def __init__(self, username, host='127.0.0.1', port=5672):
        self.username = username

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host, port=port))

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=username)

    def quit_connection(self):
        self.connection.close()

    # Function to listen for direct messages to the user
    def listen_user_queue(self, callback):
        self.channel.basic_consume(queue=self.username, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    # Function to listen for messages from a topic
    def listen_topic_queue(self, queue, callback):
        self.channel.basic_consume(queue=queue, on_message_callback=callback, auto_ack=True)

        threading.Thread(target=self.channel.start_consuming, daemon=True).start()

    # Function to send a direct message to another user
    def send_direct_message(self, destination, message):
        self.channel.basic_publish(exchange='', routing_key=destination, body=message)

    # Function to publish a message to a topic
    def publish_to_topic(self, topic, message):
        self.channel.basic_publish(exchange=topic, routing_key='', body=message)

    # Function to subscribe to a topic
    def subscribe_to_topic(self, topic, callback):
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange=topic, queue=queue_name)

        self.listen_topic_queue(queue_name, callback)

    def show_menu(self):
        threading.Thread(target=self.listen_user_queue, args=(self.username,), daemon=True).start()
    
        while True:
            print("\n1) Enviar mensagem direta")
            print("2) Publicar em tópico")
            print("3) Assinar tópico")
            print("0) Sair")
            op = input("Escolha uma opção: ")

            if op == "1":
                self.send_direct_message()
            elif op == "2":
                self.publish_to_topic()
            elif op == "3":
                self.subscribe_to_topic(self.username)
            elif op == "0":
                break