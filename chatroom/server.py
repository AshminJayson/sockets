import socket
import json
import sys
import threading
import os
from datetime import datetime


s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketAddr = ('127.0.0.1', 12345)

s.bind(socketAddr)

serverAuthorizationKey = input(
    "Input Server Authorization Key password or ENTER for default<client> : ")
if serverAuthorizationKey == '':
    serverAuthorizationKey = 'client'


print(
    "- {} listening on port {} -".format(socket.gethostname(), socketAddr[1]))


clients = {}

def formatWindow():
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[K")

def printToConsole(output):
    currentTime = datetime.now().strftime("%H:%M:%S")
    print("{} - {}".format(currentTime, output))


def listen():
    hitCount = 0
    while True:
        message, address = None, None
        try:
            message, address = s.recvfrom(1024)
        except:
            continue

        hitCount += 1
        body = json.loads(message.decode())
        status = [200, 'Served']


        if body['type'] == 'chat' and address not in clients: 
            printToConsole("Unauthorized request from : {}".format(address))
            status = [401, "Unauthorized client"]
            unicastMessage(address, "You are not allowed to send or receive chat messages", 'notification')
        else:
            if body['type'] == 'registration':
                if body['password'] != serverAuthorizationKey:
                    status = [401, "Invalid password"]
                    unicastMessage(address, 'Invalid password',
                                'notification')
                    printToConsole("Denied access to ( {} ) due to incorrect password".format(
                        body['name']))
                else:
                    clients[address] = body['name']
                    unicastMessage(address, '-- You are now in the mix --',
                                'notification')
                    printToConsole("( {} ) joined the chatroom".format(body['name']))
                    broadcastMessage(body['name'] + " joined the chat",
                                    address, 'notification')
            elif body['type'] == 'chat':
                broadcastMessage(body['message'], address, 'chat')

        printToConsole("Hit Count : {} | Last Hit from : {} | Request Type : {} | Status : {}".format(hitCount, address, body['type'], status))
        formatWindow()


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

def signalTerminate():
    print("Terminating server...")
    s.close()
    os._exit(1)

def checkTerminate():
    try:
        x = input("Press ANY KEY to terminate server \n")
        signalTerminate()
    finally:
        signalTerminate()



t1 = threading.Thread(target=listen)
t2 = threading.Thread(target=checkTerminate)

t1.start()
t2.start()

t1.join()
t2.join()
