import socket
import json

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = socket.gethostname()
socketAddr = ('127.0.0.1', 12345)

print(host)

s.bind(socketAddr)

chatRoomPassword = "d"
print("Server listening on port {}".format(socketAddr[1]))

clients = {}


def listen():
    while True:
        message, address = s.recvfrom(1024)
        msg = message.decode()
        body = json.loads(msg)

        if body['type'] == 'registration':
            if body['password'] != chatRoomPassword:
                s.sendto('Invalid password'.encode(), address)
                print("Denied access to ( {} ) due to incorrect password".format(
                    body['name']))
            else:
                clients[address] = body['name']
                print("( {} ) joined the chatroom".format(body['name']))
                sendMessage(body['name'] + " joined the chat",
                            address, 'notification')
        elif body['type'] == 'chat':
            sendMessage(body['message'], address, 'chat')


def sendMessage(msg, recAddress, messageType):

    recName = clients[recAddress]
    body = {}

    if messageType == 'notification':
        body = {'message': msg, 'author': 'server', 'type': messageType}
    elif messageType == 'chat':
        body = {'message': msg, 'author': recName, 'type': messageType}

    for clientAddress in clients:
        if clientAddress == recAddress:
            continue
        s.sendto(json.dumps(body).encode(), clientAddress)


listen()
