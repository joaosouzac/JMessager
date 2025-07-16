import tkinter as tk
import threading

from tkinter import simpledialog, scrolledtext, messagebox
from middleware.user import User


user = User(
    #simpledialog.askstring("Login", "Enter username:")
    "Augusto"
)

# Function to write to message log
def write_log(msg):
    message_log.config(state='normal')
    message_log.insert('end', msg + '\n')
    message_log.yview('end')
    message_log.config(state='disabled')


# Function to update sidebar with message counts
def update_sidebar():
    sidebar.delete(0, tk.END)

    for name, msgs in user.message_history.items():
        sidebar.insert(tk.END, f"{name} ({len(msgs)})")


# Function to show history of clicked queue/topic
def show_history(event):
    selection = sidebar.curselection()

    if not selection:
        return
    
    selected = sidebar.get(selection)
    queue_or_topic = selected.split(' (')[0]
    msgs = user.message_history.get(queue_or_topic, [])
    content = "\n".join(msgs) if msgs else "(No messages yet)"

    messagebox.showinfo(f"History: {queue_or_topic}", content)


# Function to simulate receiving a message and update sidebar
def register_message(destination, message):
    user.register_message_to_history(destination, message)

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
    msg = f"[{user.username}]: {simpledialog.askstring("Message", "Enter your message:")}"

    if dest and msg:
        user.send_direct_message(dest, msg)
        user.register_message_to_history(dest, msg)


# Function to publish a message to a topic
def publish_to_topic():
    topic = simpledialog.askstring("Topic", "Enter topic name:")
    msg = f"[{user.username}]: {simpledialog.askstring("Message", "Enter your message:")}"

    if topic and msg:
        user.publish_to_topic(topic, msg)
        user.register_message_to_history(topic, msg)


# Function to subscribe to a topic
def subscribe_to_topic():
    def callback(ch, method, properties, body):
        decoded = body.decode()
        write_log(f"[📢 Topic {topic}] {decoded}")
        register_message(topic, decoded)

    topic = simpledialog.askstring("Subscribe", "Enter topic name:")
    
    if topic:
        user.subscribe_to_topic(topic, callback)

        update_sidebar()
        
        write_log(f"✅ Subscribed to topic '{topic}'.")

# GUI Setup
root = tk.Tk()
root.title(f"Client - {user.username}")
root.geometry("800x500")

root.grid_rowconfigure(0,  weight=1)
root.grid_rowconfigure(1,  weight=3)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

# Frames
frame_log = tk.Frame(root)

frame_log.grid(
    row=0, column=0, columnspan=2, sticky="nsew", padx=10, pady=10
)
frame_log.grid_rowconfigure(0, weight=1)
frame_log.grid_columnconfigure(0, weight=1)

frame_sidebar = tk.Frame(root)

frame_sidebar.grid(
    row=1, column=0, sticky="nsew", padx=10, pady=10
)
frame_log.grid_rowconfigure(1, weight=1)
frame_log.grid_columnconfigure(0, weight=1)

frame_buttons = tk.Frame(root)

frame_buttons.grid(
    row=1, column=1, sticky="nsew", padx=10, pady=10
)
frame_log.grid_rowconfigure(3, weight=1)
frame_log.grid_columnconfigure(0, weight=1)

# Main message log area
tk.Label(frame_log, text="Log").grid(row=0, column=0)

message_log = scrolledtext.ScrolledText(frame_log, state='disabled', height=10)
message_log.grid(
    row=0, column=0, sticky="nsew"
)

# Sidebar to show queues and topics with message count
tk.Label(frame_sidebar, text="Messages").grid(row=0, column=0, pady=5)

sidebar = tk.Listbox(frame_sidebar, width=40)
sidebar.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

sidebar.bind('<<ListboxSelect>>', show_history)

# # Action buttons

tk.Button(frame_buttons, text="Send Direct Message", width=25, command=send_direct_message).grid(
    row=1, column=0, pady=5
)

tk.Button(frame_buttons, text="Publish to Topic", width=25, command=publish_to_topic).grid(
    row=2, column=0, pady=5
)

tk.Button(frame_buttons, text="Subscribe to Topic", width=25, command=subscribe_to_topic).grid(
    row=3, column=0, pady=5
)

# Start listening for direct messages
threading.Thread(target=listen_user_queue, daemon=True).start()

# Initial sidebar update
update_sidebar()

# Start GUI loop
root.mainloop()
user.quit_connection()
