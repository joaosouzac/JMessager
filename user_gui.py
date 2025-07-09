# User GUI
import tkinter as tk
import threading

from tkinter import simpledialog, scrolledtext
from middleware.user import User


def write(message):
    log.config(state="normal")
    log.insert("end", message + "\n")
    log.yview("end")
    log.config(state="disabled")

def listen_messages():
    def callback(ch, method, properties, body):
        write(f"DM: {body.decode()}")
    
    user.listen_user_queue(callback)

def listen_topic(queue_name, topic):
    def callback(ch, method, properties, body):
        write(f"Tópico {topic}: {body.decode()}")
    
    user.listen_to_topic(queue_name, callback)

def send_message():
    dest = simpledialog.askstring("Enviar para", "Usuário:")
    message = simpledialog.askstring("Mensagem", "Digite a mensagem:")

    if dest and message:
        user.send_direct_message(dest, message)

def publish_to_topic():
    topic = simpledialog.askstring("Tópico", "Nome do Tópico:")
    message = simpledialog.askstring("Mensagem", "Digite a mensagem:")

    if topic and message:
        user.publish_to_topic(topic, message)

def subscribe_to_topic():
    topic = simpledialog.askstring("Tópico", "Nome do Tópico:")

    if topic:
        user.subscribe_to_topic(topic)
        write(f"Tópico assinado com sucesso!")



user = User(
    simpledialog.askstring("Login", "Nome de Usuário")
)

app = tk.Tk()
app.title("JMessager")
app.geometry("500x400")
app.resizable(False, False)

log = scrolledtext.ScrolledText(app, state="disabled", height=15)
log.pack(padx=10, pady=5, fill="both", expand=True)

tk.Button(app, text="Send Direct Message", command=send_message).pack(fill="x")
tk.Button(app, text="Publish on Topic", command=publish_to_topic).pack(fill="x")
tk.Button(app, text="Subscribe a Topic", command=subscribe_to_topic).pack(fill="x")

threading.Thread(target=listen_messages, daemon=True).start()

app.mainloop()
user.quit_connection()