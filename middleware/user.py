import pika
import threading

class User:
    def __init__(self, username):
        self.username = username

        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=username)

    def quit_connection(self):
        self.connection.close()

    def listen_user_queue(self, callback):
        self.channel.basic_consume(queue=self.username, on_message_callback=callback, auto_ack=True)
        self.channel.start_consuming()

    def send_direct_message(self, destination, message):
        self.channel.basic_publish(exchange='', routing_key=destination, body=message)

    def publish_to_topic(self, topic, message):
        self.channel.basic_publish(exchange=topic, routing_key='', body=message)

    def subscribe_to_topic(self, topic, callback):
        result = self.channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        self.channel.queue_bind(exchange=topic, queue=queue_name)

        self.channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

        threading.Thread(target=self.channel.start_consuming, daemon=True).start()

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