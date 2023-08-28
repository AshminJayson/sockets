import socket
import threading
import json
import random
import os
import sys



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
    def __init__(self, authorizationToken, message):
        self.authorizationToken = authorizationToken
        self.message = message
        self.type = 'chat'

class Client:
    def __init__(self, socketAddress, authorizationToken, chatroomName, chatroomPassword, username):
        self.socketAddress = socketAddress
        self.authorizationToken = authorizationToken
        self.chatroomName = chatroomName
        self.chatroomPasskey = chatroomPassword
        self.username = username
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Enable this on windows
        self.s.bind(('', random.randint(1000, 10000)))

    def signalInit(self):
        print("Client intiated with username {}".format(
            self.username, self.socketAddress))
        print("Connecting to server {} ...".format(self.socketAddress))
        self._establishConnection()

    def _establishConnection(self) -> bool:
        payload = json.dumps({'username': self.username, 'authorizationToken': self.authorizationToken,
                             'chatroomName': self.chatroomName, 'chatroomPasskey': self.chatroomPasskey, 'type': 'registration'}).encode()
        self.s.sendto(payload, self.socketAddress)

        response, address = self.s.recvfrom(1024)
        responsePayload : ResponsePayload = json.loads(response.decode(), object_hook=ResponsePayload.from_json)
        print(responsePayload)


        if responsePayload.status_code != 401:
            print(responsePayload.message)
            threading.Thread(target=self._listener).start()
            threading.Thread(target=self._input).start()
        else:
            #Terminate upon invalid authentication 
            os._exit(1)

    def _listener(self):
        while True:
            response, address = self.s.recvfrom(1024)
            payload : ResponsePayload = json.loads(response.decode(), object_hook=ResponsePayload.from_json)
            print(payload.message,  payload.author)

    def _input(self):
        while True:
            message = input()
            if message == 'q()':
                self._terminateClient()
            else:
                payload = ChatPayload(authorizationToken=self.authorizationToken, message=message)
                self.s.sendto(json.dumps(payload.__dict__).encode(), self.socketAddress)

    def _terminateClient(self) -> None:
        print("Terminating client...")
        self.s.close()
        os._exit(1)


def main():
    username = input("Enter username: ")
    authorizationToken = 'd'

    socketAddr = ('127.0.0.1', 12345)
    client = Client(socketAddress=socketAddr, username=username, authorizationToken=authorizationToken, chatroomName='datteba', chatroomPassword='d')
    client.signalInit();


mainThread = threading.Thread(target=main).start()