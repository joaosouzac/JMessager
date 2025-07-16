# Broker MOM

import pika
import requests


# Configuração de autenticação da API do RabbitMQ Management
BASE_URL = "http://localhost:15672/api"


class Broker:
    def __init__(self, host='127.0.0.1', port=5672, debug=False):
        self.users = {} # Armazena os usuários cadastrados
        self.topics = set() # Armazena os nomes dos tópicos

        # Estabelece conexão com o servidor RabbitMQ (local)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host, port=port))

        # Cria canal de comunição AMQP para declarar filas, exchanges, etc.
        self.channel = self.connection.channel()

        self.debug = debug

        self.sync_amqp()
    
    def close_connection(self):
        self.connection.close()

    def sync_amqp(self, auth=('guest', 'guest')):
        queues = requests.get(f"{BASE_URL}/queues", auth=auth).json()
        exchanges = requests.get(f"{BASE_URL}/exchanges", auth=auth).json()

        self.users = {queue["name"]: [] for queue in queues}
        self.topics = {exchange["name"] for exchange in exchanges if exchange["type"] == "fanout" and exchange["name"]}

    # Seção de Gerenciamento de Usuários
    # Criar Usuário
    def create_user(self, username):
        # Verifica se usuário já existe.
        if self.debug and (username in self.users): 
            print(f"Usuário '{username}' já existe.")
            return
        
        # Cria um fila com o nome do usuário (comunicação direta)
        self.channel.queue_declare(queue=username)
        self.users[username] = []

        if self.debug:
            print(f"Usuário '{username}' criado com sucesso.")

    # Listar usuários
    def list_users(self):
        if self.debug:
            print("Usuários existentes:", list(self.users.keys()))

    # Criar tópico
    def create_topic(self, topic):
        # Verifica se o tópico já existe
        if self.debug and (topic in self.topics):
            print(f"Tópico '{topic}' já existe.")
            return
        
        # Cria uma exchange para todas as filas vinculadas
        self.channel.exchange_declare(exchange=topic, exchange_type='fanout')
        self.topics.add(topic)

        if self.debug:
            print(f"Tópico '{topic}' criado.")

    # Deletar tópico
    def delete_topic(self, topic):
        # Verifica se o tópico existe
        if self.debug and topic not in self.topics:
            print(f"Tópico '{topic}' não existe.")
            return
        
        # Remove o exchange do broker
        self.channel.exchange_delete(exchange=topic)
        self.topics.remove(topic)

        if self.debug:
            print(f"Tópico '{topic}' removido.")

    # Listar tópicos registrados
    def list_topics(self):
        if self.debug:
            print("Tópicos existentes:", list(self.topics))

    # Menu principal - Debug
    def show_menu(self):
        while self.debug:
            print("1) Criar usuário")
            print("2) Listar usuários")
            print("3) Criar tópico")
            print("4) Remover tópico")
            print("5) Listar tópicos")
            print("0) Sair")
            print("")

            op = input("Escolha uma opção: ")

            if op == "1":
                self.create_user(input("Nome do usuário: "))
            elif op == "2":
                self.list_users()
            elif op == "3":
                self.create_topic(input("Nome do tópico: "))
            elif op == "4":
                self.delete_topic(input("Nome do tópico: "))
            elif op == "5":
                self.list_topics()
            elif op == "0":
                self.close_connection()
                break
