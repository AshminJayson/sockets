import socket
import json
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketAddr = ('127.0.0.1', 12345)


s.bind(socketAddr)

chatRoomPassword = input(
    "Input chat room password or ENTER for default<client> : ")
if chatRoomPassword == '':
    chatRoomPassword = 'client'


print(
    "- {} listening on port {} -".format(socket.gethostname(), socketAddr[1]))


clients = {}


def listen():
    hitCount = 0
    while True:
        message, address = None, None
        # try:
        message, address = s.recvfrom(1024)
        hitCount += 1
        print("Hit Count : {} | Last Hit from : {}".format(hitCount, address))
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")
        # except:
        # continue

        msg = message.decode()
        body = json.loads(msg)

        if body['type'] == 'registration':
            if body['password'] != chatRoomPassword:
                unicastMessage(address, 'Invalid password',
                               'notification')
                print("Denied access to ( {} ) due to incorrect password".format(
                    body['name']))
            else:
                clients[address] = body['name']
                unicastMessage(address, '-- You are now in the mix --',
                               'notification')
                print("( {} ) joined the chatroom".format(body['name']))
                broadcastMessage(body['name'] + " joined the chat",
                                 address, 'notification')
        elif body['type'] == 'chat':
            broadcastMessage(body['message'], address, 'chat')


def unicastMessage(address, message, messageType):
    if messageType == 'notification':
        body = {'message': message, 'author': 'server', 'type': messageType}
        s.sendto(json.dumps(body).encode(), address)


def broadcastMessage(msg, recAddress, messageType):

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
