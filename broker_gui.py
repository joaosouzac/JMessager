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
    lista_usuarios.delete(0, END)
    for u in bk.users:
        lista_usuarios.insert(END, u)

    lista_topicos.delete(0, END)
    for t in bk.topics:
        lista_topicos.insert(END, t)

bk = Broker()

app = tk.Tk()
app.title("Broker Manager")

tk.Button(app, text="Criar Usuário", command=new_user).pack(fill="x")
tk.Button(app, text="Criar Tópico", command=new_topic).pack(fill="x")
tk.Button(app, text="Remover Tópico", command=remove_topic).pack(fill="x")

tk.Label(app, text="Usuários:").pack()
lista_usuarios = Listbox(app)
lista_usuarios.pack(fill="both", expand=True)

tk.Label(app, text="Tópicos:").pack()
lista_topicos = Listbox(app)
lista_topicos.pack(fill="both", expand=True)

update_list()

app.mainloop()
bk.close_connection()