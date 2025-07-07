import pika
import threading

def listen_user_queue(username):
    def callback(ch, method, properties, body):
        print(f"\n📨 Mensagem recebida: {body.decode()}")

    channel.basic_consume(queue=username, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

def send_direct_message():
    dest = input("Destinatário: ")
    msg = input("Mensagem: ")
    channel.basic_publish(exchange='', routing_key=dest, body=msg)

def publish_to_topic():
    topic = input("Tópico: ")
    msg = input("Mensagem: ")
    channel.basic_publish(exchange=topic, routing_key='', body=msg)

def subscribe_to_topic(username):
    topic = input("Tópico a assinar: ")
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange=topic, queue=queue_name)

    def callback(ch, method, properties, body):
        print(f"\n📢 [TOPICO {topic}] {body.decode()}")

    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    threading.Thread(target=channel.start_consuming, daemon=True).start()
    print(f"{username} agora assina o tópico '{topic}'.")

def user_menu(username):
    threading.Thread(target=listen_user_queue, args=(username,), daemon=True).start()
    
    while True:
        print("\n1) Enviar mensagem direta")
        print("2) Publicar em tópico")
        print("3) Assinar tópico")
        print("0) Sair")
        op = input("Escolha uma opção: ")

        if op == "1":
            send_direct_message()
        elif op == "2":
            publish_to_topic()
        elif op == "3":
            subscribe_to_topic(username)
        elif op == "0":
            break

if __name__ == "__main__":
    username = input("Digite seu nome de usuário: ")
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=username)
    user_menu(username)
    connection.close()
