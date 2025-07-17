import tkinter as tk

from tkinter import simpledialog, messagebox


def ask_connection():
    host = simpledialog.askstring("IP Address", "Enter the IP Address:")
    port = simpledialog.askinteger("Port", "Enter the Port:")

    return host, port