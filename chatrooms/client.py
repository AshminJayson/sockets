"""Program that handles the client side logic for the chatrooms"""
import socket
import threading
import json
import random
import os
import sys


def clear_console():
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[K")


class ResponsePayload():
    def __init__(self, message, type, status_code, author):
        self.message = message
        self.type = type
        self.status_code = status_code
        self.author = author

    @classmethod
    def from_json(cls, json_obj):
        return cls(json_obj['message'], json_obj['type'], json_obj['status_code'], json_obj['author'])


# class RegistrationPayload():
#     def __init__(self, username, message, authorizationToken, type):
#         self.username = username
#         self.message = message
#         self.authorizationToken = authorizationToken
#         self.type = type


class ChatPayload():
    def __init__(self, authorization_token, message):
        self.authorization_token = authorization_token
        self.message = message
        self.type = 'chat'


class Client:
    def __init__(self, socket_address, authorization_token, chatroom_name, chatroom_password, username):
        self.socket_address = socket_address
        self.authorization_token = authorization_token
        self.chatroom_name = chatroom_name
        self.chatroom_passkey = chatroom_password
        self.username = username
        self.socket_handle = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Enable this on windows
        self.socket_handle.bind(('', random.randint(1000, 10000)))

    def signal_init(self):
        print(
            f"\nClient intiated with username {self.username}")
        print(f"Connecting to server {self.socket_address} ...\n")
        self._establish_connection()

    def _establish_connection(self) -> bool:
        payload = json.dumps({'username': self.username, 'authorizationToken': self.authorization_token,
                             'chatroomName': self.chatroom_name, 'chatroomPasskey': self.chatroom_passkey, 'type': 'registration'}).encode()
        self.socket_handle.sendto(payload, self.socket_address)

        response, _ = self.socket_handle.recvfrom(1024)
        response_payload: ResponsePayload = json.loads(
            response.decode(), object_hook=ResponsePayload.from_json)

        if response_payload.status_code != 401:
            print(response_payload.message)
            threading.Thread(target=self._listener).start()
            threading.Thread(target=self._input).start()
        else:
            # Terminate upon invalid authentication
            print("Invalid authorization token...")
            os._exit(1)

    def _listener(self):
        while True:
            response, _ = self.socket_handle.recvfrom(1024)
            payload: ResponsePayload = json.loads(
                response.decode(), object_hook=ResponsePayload.from_json)
            if payload.type == 'notification':
                if payload.status_code == 501:
                    print(payload.message)
                    self._terminate_client()
            elif payload.type == 'chat':
                print(f"{payload.author} : {payload.message}")

    def _input(self):
        print("Enter q() to terminate client")
        while True:
            text = input()
            if text == 'q()':
                self._terminate_client()
            else:
                sys.stdout.write("\033[F")
                sys.stdout.write("\033[K")
                print("You:", text)
                payload = ChatPayload(
                    authorization_token=self.authorization_token, message=text)
                self.socket_handle.sendto(json.dumps(
                    payload.__dict__).encode(), self.socket_address)

    def _terminate_client(self) -> None:
        print("Terminating client...")
        self.socket_handle.close()
        os._exit(1)


def main():
    print("Heyy let's get talkin......")
    socket_address = ('127.0.0.1', 12345)

    username = input("Enter username: ")
    authorization_token = input("Enter server authorization token: ")

    print("\nEnter chatroom name and password")
    print("If chatroom does not exist, it'll then be created with the given credentials")
    chatroom_name = input("Enter chat room name: ")
    chatroom_password = input("Enter chatroom password: ")

    client = Client(socket_address=socket_address, username=username, authorization_token=authorization_token,
                    chatroom_name=chatroom_name, chatroom_password=chatroom_password)
    client.signal_init()


threading.Thread(target=main).start()
