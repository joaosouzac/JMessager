# Broker MOM

import pika
import sys


users = {} # Armazena os usuários cadastrados
topics = set() # Armazena os nomes dos tópicos

# Estabelece conexão com o servidor RabbitMQ (local)
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))

# Cria canal de comunição AMQP para declarar filas, exchanges, etc.
channel = connection.channel()

# Seção de Gerenciamento de Usuários
# Criar Usuário
def create_user(username):
    # Verifica se usuário já existe.
    if username in users: 
        print(f"Usuário '{username}' já existe.")
        return
    
    # Cria um fila com o nome do usuário (comunicação direta)
    channel.queue_declare(queue=username)
    users[username] = []

    print(f"Usuário '{username}' criado com sucesso.")

# Listar usuários
def list_users():
    print("Usuários existentes:", list(users.keys()))

# Criar tópico
def create_topic(topic):
    # Verifica se o tópico já existe
    if topic in topics:
        print(f"Tópico '{topic}' já existe.")
        return
    
    # Cria uma exchange para todas as filas vinculadas
    channel.exchange_declare(exchange=topic, exchange_type='fanout')
    topics.add(topic)

    print(f"Tópico '{topic}' criado.")

# Deletar tópico
def delete_topic(topic):
    # Verifica se o tópico existe
    if topic not in topics:
        print(f"Tópico '{topic}' não existe.")
        return
    
    # Remove o exchange do broker
    channel.exchange_delete(exchange=topic)
    topics.remove(topic)

    print(f"Tópico '{topic}' removido.")

# Listar tópicos registrados
def list_topics():
    print("Tópicos existentes:", list(topics))

# Menu principal - Debug
def broker_menu():
    while True:
        print("\n1) Criar usuário")
        print("2) Listar usuários")
        print("3) Criar tópico")
        print("4) Remover tópico")
        print("5) Listar tópicos")
        print("0) Sair")
        op = input("Escolha uma opção: ")

        if op == "1":
            create_user(input("Nome do usuário: "))
        elif op == "2":
            list_users()
        elif op == "3":
            create_topic(input("Nome do tópico: "))
        elif op == "4":
            delete_topic(input("Nome do tópico: "))
        elif op == "5":
            list_topics()
        elif op == "0":
            break

if __name__ == "__main__":
    broker_menu()
    connection.close()
