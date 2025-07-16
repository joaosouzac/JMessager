import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
import pika
import threading

from middleware.user import User


user = User(
    simpledialog.askstring("Login", "Enter username:")
)


# Dictionary to store message history by queue or topic
message_history = {
    user.username: []  # direct messages to this user
}

# GUI Setup
root = tk.Tk()
root.title(f"Client - {user.username}")
root.geometry("600x400")

# Main message log area
message_log = scrolledtext.ScrolledText(root, state='disabled', height=10)
message_log.pack(padx=10, pady=5, fill="both", expand=True)


# Sidebar to show queues and topics with message count
tk.Label(root, text="Messages").pack()

sidebar = tk.Listbox(root, width=40)
sidebar.pack(side='left', fill='y', padx=10, pady=5)


# Function to write to message log
def write_log(msg):
    message_log.config(state='normal')
    message_log.insert('end', msg + '\n')
    message_log.yview('end')
    message_log.config(state='disabled')


# Function to update sidebar with message counts
def update_sidebar():
    sidebar.delete(0, tk.END)
    for name, msgs in message_history.items():
        sidebar.insert(tk.END, f"{name} ({len(msgs)})")


# Function to show history of clicked queue/topic
def show_history(event):
    selection = sidebar.curselection()
    if not selection:
        return
    selected = sidebar.get(selection)
    queue_or_topic = selected.split(' (')[0]
    msgs = message_history.get(queue_or_topic, [])
    content = "\n".join(msgs) if msgs else "(No messages yet)"
    messagebox.showinfo(f"History: {queue_or_topic}", content)


sidebar.bind('<<ListboxSelect>>', show_history)


# Function to simulate receiving a message and update sidebar
def register_message(destination, message):
    if destination not in message_history:
        message_history[destination] = []
    message_history[destination].append(message)
    update_sidebar()


# Function to listen for direct messages to the user
def listen_user_queue():
    def callback(ch, method, properties, body):
        decoded = body.decode()
        write_log(f"[Direct] {decoded}")
        register_message(user.username, decoded)

    user.listen_user_queue(callback)

# Function to send a direct message to another user
def send_direct_message():
    dest = simpledialog.askstring("Send to", "Recipient user:")
    msg = simpledialog.askstring("Message", "Enter your message:")

    if dest and msg:
        user.send_direct_message(dest, msg)


# Function to publish a message to a topic
def publish_to_topic():
    topic = simpledialog.askstring("Topic", "Enter topic name:")
    msg = simpledialog.askstring("Message", "Enter your message:")

    if topic and msg:
        user.publish_to_topic(topic, msg)


# Function to subscribe to a topic
def subscribe_to_topic():
    def callback(ch, method, properties, body):
        decoded = body.decode()
        write_log(f"[📢 Topic {topic}] {decoded}")
        register_message(topic, decoded)

    topic = simpledialog.askstring("Subscribe", "Enter topic name:")
    
    if topic:
        user.subscribe_to_topic(topic, callback)

        message_history[topic] = []
        update_sidebar()
        
        write_log(f"✅ Subscribed to topic '{topic}'.")


# Action buttons
frame_buttons = tk.Frame(root)
frame_buttons.pack(side='right', padx=10, pady=10)

tk.Button(frame_buttons, text="Send Direct Message", width=25, command=send_direct_message).pack(pady=5)
tk.Button(frame_buttons, text="Publish to Topic", width=25, command=publish_to_topic).pack(pady=5)
tk.Button(frame_buttons, text="Subscribe to Topic", width=25, command=subscribe_to_topic).pack(pady=5)


# Start listening for direct messages
threading.Thread(target=listen_user_queue, daemon=True).start()

# Initial sidebar update
update_sidebar()

# Start GUI loop
root.mainloop()
user.quit_connection()
