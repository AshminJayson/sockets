"""Program that handles the server side logic for the chatrooms"""
import socket
import threading
import os
import json
import time
from typing import Dict
import sys
from rich.console import Console


console = Console(stderr=True)
serverlog = Console(stderr=True, record=True)


def clear_console():
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[K")


def print_to_console(output, type="default"):
    if type == "default":
        serverlog.log(output)
    elif type == "chatroom broadcast":
        serverlog.log(f"[blue]{output}")
    elif type == "invalid authentication":
        serverlog.log(f"[red]{output}")
    elif type == "registration":
        serverlog.log(f"[green]{output}")
    elif type == "unicast":
        serverlog.log(f"[cyan]{output}")
    elif type == "broadcast":
        serverlog.log(f"[magenta]{output}")


def write_server_log_to_file():
    file_handle = open("log.txt", "w")
    log = serverlog.export_text()
    file_handle.write(log)
    file_handle.close()


# Models
class MessagePayload():
    def __init__(self, message, type, status_code, author):
        self.message = message
        self.type = type
        self.status_code = status_code
        self.author = author


# Add class that handles chatroom logic
class ChatRoom():
    # Initialize chatroom with name, passkey and clients list
    def __init__(self, chatroom_name, passkey) -> None:
        self.chatroom_name = chatroom_name
        self.passkey = passkey
        self.clients: Dict[tuple: str] = {}

    # Function to add new client
    def add_client(self, client_address: tuple, client_name: str):
        self.clients[client_address] = client_name

    def message_chat(self, client_address, payload: MessagePayload, server_socket: socket.socket):
        print_to_console(
            f"Broadcasting message from {self.clients[client_address]} to all clients in chatroom {self.chatroom_name}...", "chatroom broadcast")
        for client_address_iter in self.clients:
            if client_address_iter == client_address:
                continue
            server_socket.sendto(json.dumps(
                payload.__dict__).encode(), client_address_iter)


# Implement master thread and tunneling interface
class Master():
    # Socket Initializer
    def __init__(self, socket_address, authorization_token) -> None:
        self.socket_handle: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM)
        self.hostname = socket.gethostname()
        self.socket_address = socket_address
        self.authorization_token = authorization_token
        self.chatrooms: Dict[tuple: ChatRoom] = {}

        # For identification of chatroom in a chat type request
        self.clients: Dict[tuple: ChatRoom] = {}
        self.hitcount = 0
        # Bind server to socket
        self.socket_handle.bind(self.socket_address)

        # Thread for client listener
        threading.Thread(target=self._listener).start()
        self._signal_init()
        # Thread for listening to input
        threading.Thread(target=self._check_terminate).start()

    def _signal_init(self) -> None:
        with console.status("Starting server..."):
            time.sleep(.5)
        print_to_console(
            f"{self.hostname} listening on port {self.socket_address} | Authorization Token : {self.authorization_token}")

    def _check_terminate(self) -> None:
        try:
            console.input(
                "[red]Press ANY KEY to terminate server[/red] \n")
        finally:
            self._broadcast(MessagePayload(
                "Server is being terminated", "notification", 501, "server"))
            write_server_log_to_file()
            print_to_console("Terminating server...")
            self.socket_handle.close()
            os._exit(1)

    # Master listener

    def _listener(self):
        while True:
            request, client_address = None, None
            try:
                request, client_address = self.socket_handle.recvfrom(1024)
            except Exception as ex:
                # Some random due to client, reset connection
                print_to_console(f"{ex} on _listener")
                continue

            self.hitcount += 1
            payload = json.loads(request.decode())
            print_to_console(
                f"{payload['type']} request recieved from {client_address}")

            # Check authorization for every request
            if not self._authorize_request(payload['authorizationToken']):
                # Handle invalid authorization
                print_to_console(
                    f"Invalid authorization token from {client_address}", "invalid authentication")
                self._unicast(
                    client_address, MessagePayload('Invalid authorization token : Authentication Failed', 'notification', 401, 'server'))
                continue

            if payload['type'] == 'registration':
                self._registrations_handler(payload, client_address)
            elif payload['type'] == 'chat':
                self._chat_handler(payload, client_address)

    def _authorize_request(self, authorization_token) -> bool:
        return self.authorization_token == authorization_token

    def _registrations_handler(self, payload, client_address):
        print_to_console(
            f"Registering Client {client_address} ...", "registration")
        client_name, chatroom_name, chatroom_passkey = payload[
            'username'], payload['chatroomName'], payload['chatroomPasskey']
        self._authorize_or_generate_chatroom_request(
            chatroom_name, client_address, client_name, chatroom_passkey)

    # Provision chatrooms
    def _authorize_or_generate_chatroom_request(self, chatroom_name, client_address, client_name, chatroom_passkey) -> None:
        if chatroom_name in self.chatrooms:
            chatroom: ChatRoom = self.chatrooms[chatroom_name]
            if chatroom.passkey == chatroom_passkey:
                chatroom.add_client(client_address, client_name)
                self.clients[client_address] = chatroom
                print_to_console(
                    f"{client_name} - {client_address} has joined chat room {chatroom_name}", "registration")
                payload = MessagePayload(
                    f"You've joined the chatroom {chatroom_name}", 'notification', 200, 'server')
                self._unicast(client_address, payload)
            else:
                print_to_console(
                    f"Invalid chatroom passkey recieved from client {client_address} - {client_name}", "invalid authentication")
                payload = MessagePayload(
                    "Invalid chatroom passkey", "notification", 401, "server")
                self._unicast(
                    client_address, payload)
        else:
            chatroom: ChatRoom = ChatRoom(
                chatroom_name, chatroom_passkey)
            chatroom.add_client(client_address, client_name)
            self.chatrooms[chatroom_name] = chatroom
            self.clients[client_address] = chatroom
            print_to_console(
                f"Chatroom {chatroom_name} has been registered", "registration")
            payload = MessagePayload(
                f"Chatroom {chatroom_name} has been registered upon request from {client_address}", 'notification', 200, 'server')
            self._unicast(client_address=client_address, payload=payload)

    # Tunneling interface / chatHandler
    def _chat_handler(self, payload, client_address):
        if client_address not in self.clients:
            print_to_console(
                f"Unregistered client {client_address} denied from access to chat handler", "invalid authentication")
            return

        message = payload['message']
        chatroom: ChatRoom = self.clients[client_address]
        client_name = chatroom.clients[client_address]
        message_payload = MessagePayload(message, 'chat', '', client_name)
        chatroom.message_chat(
            client_address, message_payload, self.socket_handle)

    # Unicast messaging function
    def _unicast(self, client_address, payload: MessagePayload):
        print_to_console(
            f"Unicast message sent to {client_address}", "unicast")
        self.socket_handle.sendto(json.dumps(
            payload.__dict__).encode(), client_address)

    # Broadcast messging function
    def _broadcast(self, payload: MessagePayload):
        print_to_console(
            f"Broadcasting notification [{payload.message}] to all chatrooms", "broadcast")
        for client_address in self.clients.keys():
            self.socket_handle.sendto(json.dumps(
                payload.__dict__).encode(), client_address)


def main():
    """Function to initialize master thread and server object"""
    console.rule("[bold blue]Chatroom Server")
    socket_addr = ('127.0.0.1', 12345)
    authorization_token = console.input(
        "\nEnter server [i red]authorization token[/i red] or press [i blue]ENTER[/i blue] for default<admin>: ")
    if authorization_token == '':
        authorization_token = 'admin'
    Master(socket_address=socket_addr,
           authorization_token=authorization_token)


main()
