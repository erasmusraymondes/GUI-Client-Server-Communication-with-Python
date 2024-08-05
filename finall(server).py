import socket
import threading

class ChatServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = None
        self.clients = {}
        self.client_names = {}

    def start_server(self):
        # Create a socket object
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to the address and port
        self.server_socket.bind((self.host, self.port))
        # Enable the server to accept connections
        self.server_socket.listen(5)
        print(f"Server started and listening on {self.host}:{self.port}")

        while True:
            # Accept a connection from a client
            client_socket, client_address = self.server_socket.accept()
            print(f"Connection established with {client_address}")

            # Start a thread to handle client communication
            threading.Thread(target=self.handle_client, args=(client_socket, client_address)).start()

    def handle_client(self, client_socket, client_address):
        client_name = client_socket.recv(1024).decode()
        self.clients[client_socket] = client_address
        self.client_names[client_socket] = client_name

        welcome_message = f"{client_name} has joined the chat."
        self.broadcast_message(client_socket, welcome_message)

        # Start a thread to handle server input
        threading.Thread(target=self.handle_server_input, args=(client_socket,)).start()

        while True:
            try:
                # Receive data from the client
                message = client_socket.recv(1024)
                if not message:
                    break

                decoded_message = message.decode()
                self.print_message(f"[{self.client_names[client_socket]}] {decoded_message}")
                self.broadcast_message(client_socket, f"[{self.client_names[client_socket]}] {decoded_message}")
            except Exception as e:
                print(f"An error occurred: {e}")
                break

        client_socket.close()
        del self.clients[client_socket]
        del self.client_names[client_socket]

    def handle_server_input(self, client_socket):
        while True:
            try:
                # Prompt server to send a message back to the client
                server_message = input("Type your message to client: ")
                if server_message.lower() == 'exit':
                    break
                self.send_message(client_socket, f"[Server] {server_message}")
            except Exception as e:
                print(f"An error occurred while sending message: {e}")
                break

    def broadcast_message(self, sender_socket, message):
        for client in self.clients.keys():
            if client != sender_socket:
                try:
                    client.sendall(message.encode())
                except Exception as e:
                    print(f"An error occurred while broadcasting: {e}")

    def send_message(self, client_socket, message):
        try:
            client_socket.sendall(message.encode())
        except Exception as e:
            print(f"An error occurred while sending message to client: {e}")

    def receive_messages(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode()
                if message:
                    # Print the received message on the server's command prompt
                    self.print_message(f"[{self.client_names[client_socket]}] {message}")
                    # Broadcast the received message to other clients
                    self.broadcast_message(client_socket, f"[{self.client_names[client_socket]}] {message}")
                else:
                    # Client has disconnected
                    self.handle_client_disconnection(client_socket)
                    break   
            except Exception as e:
                print(f"An error occurred: {e}")
                self.handle_client_disconnection(client_socket)
                break
    
    def print_message(self, message):
        print(message)  # Print the message on the server's command prompt


if __name__ == "__main__":
    host = '127.0.0.1'  # Host to bind the server, using localhost
    port = 12345        # Port to bind the server (customizable)
    
    server = ChatServer(host, port)
    server.start_server()
