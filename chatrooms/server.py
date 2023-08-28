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


def consoleClear():
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[K")


def printToConsole(output, type="default"):
    if type == "default":
        serverlog.log(output)
    elif type == "chatroom broadcast":
        serverlog.log("[blue]{}".format(output))
    elif type == "invalid authentication":
        serverlog.log("[red]{}".format(output))
    elif type == "registration":
        serverlog.log("[green]{}".format(output))
    elif type == "unicast":
        serverlog.log("[cyan]{}".format(output))
    elif type == "broadcast":
        serverlog.log("[magenta]{}".format(output))


def writeServerLogToFile():
    f = open("log.txt", "w")
    log = serverlog.export_text()
    f.write(log)
    f.close()


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
    def __init__(self, chatroomName, passkey) -> None:
        self.chatroomName = chatroomName
        self.passkey = passkey
        self.clients: Dict[tuple: str] = {}

    # Function to add new client
    def addClient(self, clientAddress: tuple, clientName: str):
        self.clients[clientAddress] = clientName

    def broadcastInChat(self, clientAddress, payload: MessagePayload, serverSocket: socket.socket):
        printToConsole("Broadcasting message from {} to all clients in chatroom {}...".format(
            self.clients[clientAddress], self.chatroomName), "chatroom broadcast")
        for clientAddressIter in self.clients:
            if clientAddressIter == clientAddress:
                continue
            serverSocket.sendto(json.dumps(
                payload.__dict__).encode(), clientAddressIter)


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
        self._signalInit()
        # Thread for listening to input
        threading.Thread(target=self._checkTerminate).start()

    def _signalInit(self) -> None:
        with console.status("Starting server..."):
            time.sleep(.5)
        printToConsole("{} listening on port {} | Authorization Token : {}".format(
            self.hostname, self.socketAddress[1], self.authorizationToken))

    def _checkTerminate(self) -> None:
        try:
            console.input(
                "[red]Press ANY KEY to terminate server[/red] \n")
        finally:
            self._broadcast(MessagePayload(
                "Server is being terminated", "notification", 501, "server"))
            writeServerLogToFile()
            printToConsole("Terminating server...")
            self.s.close()
            os._exit(1)

    # Master listener

    def _listener(self):
        while True:
            request, clientAddress = None, None
            try:
                request, clientAddress = self.s.recvfrom(1024)
            except Exception as ex:
                # Some random due to client, reset connection
                printToConsole("{} on _listener".format(ex))
                continue

            self.hitcount += 1
            payload = json.loads(request.decode())
            printToConsole("{} request recieved from {}".format(
                payload['type'], clientAddress))

            # Check authorization for every request
            if not self._authorizeRequest(payload['authorizationToken']):
                # Handle invalid authorization
                printToConsole(
                    "Invalid authorization token from {}".format(clientAddress), "invalid authentication")
                self._unicast(
                    clientAddress, MessagePayload('Invalid authorization token : Authentication Failed', 'notification', 401, 'server'))
                continue

            if payload['type'] == 'registration':
                self._registrationsHandler(payload, clientAddress)
            elif payload['type'] == 'chat':
                self._chatHandler(payload, clientAddress)

    def _authorizeRequest(self, authorizationToken) -> bool:
        return self.authorizationToken == authorizationToken

    def _registrationsHandler(self, payload, clientAddress):
        printToConsole("Registering Client {} ...".format(
            clientAddress), "registration")
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
                printToConsole(
                    "{} - {} has joined chat room {}".format(clientName, clientAddress, chatroomName), "registration")
                payload = MessagePayload("You've joined the chatroom {}".format(
                    chatroomName), 'notification', 200, 'server')
                self._unicast(clientAddress, payload)
            else:
                printToConsole(
                    "Invalid chatroom passkey recieved from client {} - {}".format(clientAddress, clientName), "invalid authentication")
                payload = MessagePayload(
                    "Invalid chatroom passkey", "notification", 401, "server")
                self._unicast(
                    clientAddress, payload)
        else:
            chatroomObj: ChatRoom = ChatRoom(
                chatroomName, chatroomPasskey)
            chatroomObj.addClient(clientAddress, clientName)
            self.chatrooms[chatroomName] = chatroomObj
            self.clients[clientAddress] = chatroomObj
            printToConsole(
                "Chatroom {} has been registered".format(chatroomName), "registration")
            payload = MessagePayload("Chatroom {} has been registered upon request from {}".format(
                chatroomName, clientAddress), 'notification', 200, 'server')
            self._unicast(clientAddress=clientAddress, payload=payload)

    # Tunneling interface / chatHandler
    def _chatHandler(self, payload, clientAddress):
        if clientAddress not in self.clients:
            printToConsole(
                "Unregistered client {} denied from access to chat handler".format(clientAddress), "invalid authentication")
            return

        message = payload['message']
        chatroomObj: ChatRoom = self.clients[clientAddress]
        clientName = chatroomObj.clients[clientAddress]
        messagePayload = MessagePayload(message, 'chat', '', clientName)
        chatroomObj.broadcastInChat(clientAddress, messagePayload, self.s)

    # Unicast messaging function
    def _unicast(self, clientAddress, payload: MessagePayload):
        printToConsole("Unicast message sent to {}".format(
            clientAddress), "unicast")
        self.s.sendto(json.dumps(payload.__dict__).encode(), clientAddress)

    # Broadcast messging function
    def _broadcast(self, payload: MessagePayload):
        printToConsole(
            "Broadcasting notification [{}] to all chatrooms".format(payload.message), "broadcast")
        for clientAddress in self.clients.keys():
            self.s.sendto(json.dumps(
                payload.__dict__).encode(), clientAddress)


def main():
    console.rule("[bold blue]Chatroom Server")
    socketAddr = ('127.0.0.1', 12345)
    authorizationToken = console.input(
        "\nEnter server [i red]authorization token[/i red] or press [i blue]ENTER[/i blue] for default<admin>: ")
    if authorizationToken == '':
        authorizationToken = 'admin'
    master = Master(socketAddress=socketAddr,
                    authorizationToken=authorizationToken)


main()
