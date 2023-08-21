import socket
import threading
import os
import time
import json
from datetime import datetime
from typing import Dict


# ----- Logic View-----
# Add class that handles chatroom logic
class ChatRoom():
    # Initialize chatroom with name, passkey and clients list
    def __init__(self, chatroomName, passkey) -> None:
        self.chatroomName = chatroomName
        self.passkey = passkey
        self.clients: Dict[tuple: str] = {}

    # Function to add new client
    def addClient(self, clientAddress: tuple, clientName: str):
        self.clients[clientAddress] = clientName


# Unicast messaging function
# Broadcast messging function


# Implement master thread and tunneling interface

class Master():
    # Socket Initializer
    def __init__(self, socketAddr, authorizationToken) -> None:
        self.s: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM)
        self.hostname = socket.gethostname()
        self.socketAddr = socketAddr
        self.authorizationToken = authorizationToken
        self.chatrooms: Dict[tuple: ChatRoom] = {}

        # For identification of chatroom in a chat type request
        self.clients: Dict[tuple: ChatRoom] = {}
        self.hitcount = 0
        # Bind server to socket
        self.s.bind(self.socketAddr)

        # Thread for client listener
        threading.Thread(target=self._listener).start()
        # Thread for listening to input
        threading.Thread(target=self._checkTerminate).start()
        self._signalInit()

    def _signalInit(self) -> None:
        print(
            "- {} listening on port {} -".format(self.hostname, self.socketAddr[1]))

    def _checkTerminate(self) -> None:
        try:
            input("Press ANY KEY to terminate server \n")
        finally:
            print("Terminating server...")
            self.s.close()
            os._exit(1)

    # Master listener

    def _listener(self):
        while True:
            request, clientAddress = None, None
            # try:
            request, clientAddress = self.s.recvfrom(1024)
            # except:
            # Some random due to client, reset connection
            # continue

            self.hitcount += 1
            payload = json.loads(request.decode())
            print(payload, clientAddress)

            # Check authorization for every request
            if not self._authorizeRequest(payload['AuthorizationToken']):
                # Handle invalid authorization
                print("Invalid authorization")
                continue

            if payload['type'] == 'registration':
                self._registrationsHandler(payload, clientAddress)
            elif payload['type'] == 'chat':
                self._chatHandler(payload, clientAddress, 'chat')

    def _authorizeRequest(self, authorizationToken) -> bool:
        return self.authorizationToken == authorizationToken

    def _registrationsHandler(self, payload, clientAddress):
        clientName, chatroomName, chatroomPasskey = payload[
            'username'], payload['chatroomName'], payload['chatroomPasskey']
        self._authorizeOrGenerateChatRoomRequest(
            chatroomName, clientAddress, clientName, chatroomPasskey)

    # Provision chatrooms
    def _authorizeOrGenerateChatRoomRequest(self, chatroomName, clientAddress, clientName, chatroomPasskey) -> None:
        if chatroomName in self.chatrooms:
            chatroomObj: ChatRoom = self.chatrooms[chatroomName]
            if chatroomObj.passkey == chatroomPasskey:
                chatroomObj.addClient(clientAddress, clientName)
                self.clients[clientAddress] = chatroomObj
            else:
                print("Invalid chatroom passkey")
        else:
            chatroomObj: ChatRoom = ChatRoom(
                chatroomName, chatroomPasskey)
            chatroomObj.addClient(clientAddress, clientName)
            self.chatrooms[chatroomName] = chatroomObj
            self.clients[clientAddress] = chatroomObj

        print(self.chatrooms, self.clients)

    # Tunneling interface / chatHandler

    def _chatHandler(self, payload, clientAddress, messageType):
        if clientAddress not in self.clients:
            print("Unregistered client")
            return

        message = payload['message']
        chatroomObj: ChatRoom = self.clients[clientAddress]
        self._broadcast(clientAddress, message, 'chat', chatroomObj)

    def _unicast(self, clientAddress, message): pass

    def _broadcast(self, clientAddress, message, messageType, chatroomObj: ChatRoom):
        clientName = chatroomObj.clients[clientAddress]
        reponsePayload = {}
        if messageType == 'notification':
            reponsePayload = {'message': message,
                              'author': 'server', 'type': messageType}
        elif messageType == 'chat':
            reponsePayload = {'message': message,
                              'author': clientName, 'type': messageType}

        for clientAddress in self.clients:
            if clientAddress == clientAddress:
                continue

        self.socketHead.sendto(json.dumps(
            reponsePayload).encode(), clientAddress)


def main():
    socketAddr = ('127.0.0.1', 12345)
    master = Master(socketAddr, 'd')


main()
