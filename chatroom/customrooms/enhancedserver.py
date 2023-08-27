import socket
import threading
import os
import time
import json
from datetime import datetime
from typing import Dict


class MessagePayload():
    def __init__(self, message, type, status_code, author):
        self.message = message
        self.type = type
        self.status_code = status_code
        self.author = author

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
    def __init__(self, socketAddress, authorizationToken) -> None:
        self.s: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM)
        self.hostname = socket.gethostname()
        self.socketAddress = socketAddress
        self.authorizationToken = authorizationToken
        self.chatrooms: Dict[tuple: ChatRoom] = {}

        # For identification of chatroom in a chat type request
        self.clients: Dict[tuple: ChatRoom] = {}
        self.hitcount = 0
        # Bind server to socket
        self.s.bind(self.socketAddress)

        # Thread for client listener
        threading.Thread(target=self._listener).start()
        # Thread for listening to input
        threading.Thread(target=self._checkTerminate).start()
        self._signalInit()

    def _signalInit(self) -> None:
        print(
            "- {} listening on port {} -".format(self.hostname, self.socketAddress[1]))

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
            if not self._authorizeRequest(payload['authorizationToken']):
                # Handle invalid authorization
                print("Invalid authorization")
                self._unicast(
                    clientAddress, 'Invalid authorization token : Authentication Failed', 'notification')
                continue

            if payload['type'] == 'registration':
                self._registrationsHandler(payload, clientAddress)
            elif payload['type'] == 'chat':
                self._chatHandler(payload, clientAddress, 'chat')

    def _authorizeRequest(self, authorizationToken) -> bool:
        return self.authorizationToken == authorizationToken

    def _registrationsHandler(self, payload, clientAddress):
        print("Registering Client...")
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
                payload = MessagePayload("You've joined the chatroom {}".format(chatroomName), 'notification', 200, 'server')
                self._unicast(clientAddress, payload)
            else:
                payload = MessagePayload("Invalid chatroom passkey", "notification")
                print("Invalid chatroom passkey")
                self._unicast(
                    clientAddress, payload)
        else:
            chatroomObj: ChatRoom = ChatRoom(
                chatroomName, chatroomPasskey)
            chatroomObj.addClient(clientAddress, clientName)
            self.chatrooms[chatroomName] = chatroomObj
            self.clients[clientAddress] = chatroomObj
            payload = MessagePayload("Chatroom {} has been registered".format(chatroomName), 'notification', 200, 'server')
            self._unicast(clientAddress=clientAddress, payload=payload)
        print(self.chatrooms, self.clients)

    # Tunneling interface / chatHandler
    def _chatHandler(self, payload, clientAddress, messageType):
        if clientAddress not in self.clients:
            print("Unregistered client")
            return

        message = payload['message']
        chatroomObj: ChatRoom = self.clients[clientAddress]
        clientName = chatroomObj.clients[clientAddress]
        messagePayload = MessagePayload(message, 'chat', '', clientName)
        self._broadcast(clientAddress, messagePayload, chatroomObj)

    def _unicast(self, clientAddress, payload: MessagePayload):
        print("Unicast message being send...")
        self.s.sendto(json.dumps(payload.__dict__).encode(), clientAddress)

    def _broadcast(self, clientAddress, payload: MessagePayload, chatroomObj: ChatRoom):
        print("Broadcasting message...")
        for clientAddressIter in chatroomObj.clients:
            if clientAddressIter == clientAddress:
                continue
            print('Client Address', clientAddressIter)
            self.s.sendto(json.dumps(
                payload.__dict__).encode(), clientAddressIter)


def main():
    socketAddr = ('127.0.0.1', 12345)
    master = Master(socketAddr, 'd')


main()
