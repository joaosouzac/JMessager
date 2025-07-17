from tkinter import simpledialog


def ask_connection():
    host = simpledialog.askstring("IP Address", "Enter the IP Address:")
    port = simpledialog.askinteger("Port", "Enter the Port:")

    return host, port