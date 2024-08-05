import tkinter as tk
from tkinter import messagebox
import socket
import threading

class ChatClient:
    def __init__(self, root):
        self.root = root
        self.root.title("CommBOX")
        self.root.geometry("600x600")

        self.name = None
        self.sock = None
        self.receive_thread = None

        self.create_ip_port_page()

    def create_ip_port_page(self):
        self.clear_widgets()
        tk.Label(self.root, text="").pack()  # Add 2 row space above
        tk.Label(self.root, text="CommBOX", font=("Goudy Stout", 20, "bold")).pack()  # Add sub-title

        self.ip_label = tk.Label(self.root, text="IP Address:")
        self.ip_label.pack()

        self.ip_entry = tk.Entry(self.root, width=30)
        self.ip_entry.pack()

        self.port_label = tk.Label(self.root, text="Port:")
        self.port_label.pack()

        self.port_entry = tk.Entry(self.root, width=30)
        self.port_entry.pack()

        self.connect_button = tk.Button(self.root, text="Connect", command=self.connect)
        self.connect_button.pack(pady=10)

    def create_name_page(self):
        self.clear_widgets()
        self.name_label = tk.Label(self.root, text="Enter Your Name:")
        self.name_label.pack(pady=10)

        self.name_entry = tk.Entry(self.root, width=30)
        self.name_entry.pack()

        self.name_button = tk.Button(self.root, text="Submit", command=self.set_name)
        self.name_button.pack(pady=10)

    def create_chat_page(self):
        self.clear_widgets()
        self.chat_label = tk.Label(self.root, text="Type Your Message Here:")
        self.chat_label.pack(pady=10)

        self.chat_text = tk.Text(self.root, width=70, height=10, wrap=tk.WORD)
        self.chat_text.pack()

        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.pack()

        self.message_box = tk.Text(self.root, width=70, height=10, wrap=tk.WORD)
        self.message_box.pack()
        self.message_box.config(state=tk.DISABLED)

    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()    #method in Tkinter is used to remove a widget from the window

    def connect(self):
        ip = self.ip_entry.get()
        port_str = self.port_entry.get()

        if not ip or not port_str:
            messagebox.showerror("Error", "IP Address and Port are required.")
            return

        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Error", "Port must be a valid integer.")
            return

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((ip, port))
            self.create_name_page()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")

    def set_name(self):
        self.name = self.name_entry.get().strip()
        if not self.name:
            messagebox.showerror("Error", "Name cannot be empty.")
            return
        try:
            self.sock.sendall(self.name.encode())
            self.create_chat_page()
            self.message_box.config(state=tk.NORMAL)
            self.message_box.insert(tk.END, f"Connected to server. Your name is {self.name}.\n")
            self.message_box.config(state=tk.DISABLED)
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send name: {str(e)}")

    def send_message(self):
        if not self.sock:
            messagebox.showerror("Error", "Please connect to a server first.")
            return

        message = self.chat_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Warning", "Cannot send an empty message.")
            return

        try:
            self.sock.sendall(message.encode())
            self.message_box.config(state=tk.NORMAL)
            self.message_box.insert(tk.END, f"[{self.name}] {message}\n")
            self.message_box.config(state=tk.DISABLED)
            self.chat_text.delete("1.0", tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {str(e)}")

    def receive_messages(self):
        while True:
            try:
                message = self.sock.recv(1024).decode()
                if message:
                    self.message_box.config(state=tk.NORMAL)
                    self.message_box.insert(tk.END, f"{message}\n")
                    self.message_box.config(state=tk.DISABLED)
                else:
                    self.message_box.config(state=tk.NORMAL)
                    self.message_box.insert(tk.END, "[Server] Disconnected\n")
                    self.message_box.config(state=tk.DISABLED)
                    break
            except Exception as e:
                self.message_box.config(state=tk.NORMAL)
                self.message_box.insert(tk.END, f"[Error] {str(e)}\n")
                self.message_box.config(state=tk.DISABLED)
                break

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    app.run()
