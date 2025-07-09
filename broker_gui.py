# Broker GUI

import tkinter as tk

from tkinter import messagebox, simpledialog, Listbox, END
from middleware.broker import Broker


# Manage Broker Methods
def new_user():
    username = simpledialog.askstring("Novo Usuário", "Digite o nome do usuário:")

    if not username:
        return
    
    if username in bk.users:
        messagebox.showwarning("Erro", f"Usuário '{username}' já existe.")
        return
    
    bk.create_user(username)

    update_list()

    messagebox.showinfo("Sucesso", f"Usuário '{username}' criado.")

def new_topic():
    topic = simpledialog.askstring("Novo Tópico", "Digite o nome do tópico:")

    if not topic:
        return
    if topic in bk.topics:
        messagebox.showwarning("Erro", f"Tópico '{topic}' já existe.")
        return
    
    bk.create_topic(topic)

    update_list()

def remove_topic():
    topic = simpledialog.askstring("Remover Tópico", "Nome do tópico:")

    if not topic or topic not in bk.topics:
        messagebox.showwarning("Erro", f"Tópico '{topic}' não existe.")
        return
    
    bk.delete_topic(topic)

    update_list()

def update_list():
    users_list.delete(0, END)
    for user in sorted(bk.users.keys()):
        users_list.insert(END, user)

    topics_list.delete(0, END)
    for topic in sorted(bk.topics):
        topics_list.insert(END, topic)

bk = Broker()

app = tk.Tk()
app.title("Broker Manager")
app.geometry("500x400")
app.resizable(False, False)

# Frame das Listas
frame_lists = tk.Frame(app)
frame_lists.pack(fill="both", expand=True, padx=10, pady=10)

# Lista de Usuários
tk.Label(frame_lists, text="Users").grid(row=0, column=0, sticky="w")

users_list = tk.Listbox(frame_lists, height=10, width=30)
users_list.grid(row=1, column=0, padx=5)

# Lista de Tópicos
tk.Label(frame_lists, text="Topics").grid(row=0, column=1, sticky="w")

topics_list = tk.Listbox(frame_lists, height=10, width=30)
topics_list.grid(row=1, column=1, padx=5)

# Frame dos botões
frame_buttons = tk.Frame(app)
frame_buttons.pack(pady=10)

# User Buttons
tk.Button(frame_buttons, text="New User", command=new_user, width=20).grid(
    row=0, column=0, padx=5, pady=5
)
tk.Button(frame_buttons, text="New Topic", command=new_topic, width=20).grid(
    row=0, column=1, padx=5, pady=5
)
tk.Button(frame_buttons, text="Remove Topic", command=remove_topic, width=20).grid(
    row=1, column=0, columnspan=2, pady=5
)

update_list()

app.mainloop()
bk.close_connection()