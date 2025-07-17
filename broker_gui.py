# Broker GUI

import tkinter as tk

from tkinter import messagebox, simpledialog, END
from middleware.broker import Broker
from popup_gui import ask_connection


# ------------- Broker Management Methods -------------------
def new_user():
    username = simpledialog.askstring("New User", "Enter username:")

    if not username:
        return
    
    if username in bk.users:
        messagebox.showwarning("Error", f"User '{username}' already exists.")
        return
    
    bk.create_user(username)

    update_list()

    messagebox.showinfo("Success", f"User '{username}' created.")

def new_topic():
    topic = simpledialog.askstring("New Topic", "Enter topic name:")

    if not topic:
        return
    
    if topic in bk.topics:
        messagebox.showwarning("Error", f"Topic '{topic}' already exists.")
        return
    
    bk.create_topic(topic)

    update_list()

def remove_topic():
    topic = simpledialog.askstring("Remove Topic", "Topic name:")

    if not topic or topic not in bk.topics:
        messagebox.showwarning("Error", f"Topic '{topic}' does not exist.")
        return
    
    bk.delete_topic(topic)

    update_list()

def update_list():
    # Update user list
    users_list.delete(0, END)
    for user in sorted(bk.users.keys()):
        users_list.insert(END, user)

    # Update topic list
    topics_list.delete(0, END)
    for topic in sorted(bk.topics):
        topics_list.insert(END, topic)

# ------------- GUI Configuration -------------------
bk_host, bk_port = ask_connection()

bk = Broker(bk_host, bk_port)

app = tk.Tk()
app.title("Broker Manager")
app.geometry("500x400")
app.resizable(False, False)

# User / Topic Frames
frame_users = tk.Frame(app)
frame_users.pack(side="left", fill="both", expand=True, padx=10, pady=10)

frame_topics = tk.Frame(app)
frame_topics.pack(side="right", fill="both", expand=True, padx=10, pady=10)

# Users Frame - Label, List, Buttons
tk.Label(frame_users, text="Users").grid(row=0, column=0, sticky="w")

users_list = tk.Listbox(frame_users, height=10, width=30)
users_list.grid(row=1, column=0, padx=5)

tk.Button(frame_users, text="New User", command=new_user, width=20).grid(
    row=2, column=0, padx=5, pady=5
)

# Topics Frame - Label, List, Buttons
tk.Label(frame_topics, text="Topics").grid(row=0, column=0, sticky="w")

topics_list = tk.Listbox(frame_topics, height=10, width=30)
topics_list.grid(row=1, column=0, padx=5)

tk.Button(frame_topics, text="New Topic", command=new_topic, width=20).grid(
    row=2, column=0, padx=5, pady=5
)
tk.Button(frame_topics, text="Remove Topic", command=remove_topic, width=20).grid(
    row=3, column=0, columnspan=2, pady=5
)

# Initializes lists on startup
update_list()

# Starts GUI loop
app.mainloop()

# Closes broker connection on exit
bk.close_connection()