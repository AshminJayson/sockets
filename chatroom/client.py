import socket
import threading
import json
import random

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketAddress = ('127.0.0.1', 12345)
# s.bind(('', random.randint(1000, 10000)))  # Enable this on windows


def listen():
    while True:
        message, address = s.recvfrom(1024)
        body = json.loads(message.decode())
        if body['type'] == 'notification':
            printToConsole(body['message'])
        else:
            printToConsole('{}: {}'.format(body['author'], body['message']))


def printToConsole(message):
    print("\n", message)


def handleInput():
    name = input("Enter you name:")
    password = input("Enter passkey:")

    body = {
        'name': name,
        'password': password,
        'type': 'registration'
    }

    s.sendto(json.dumps(body).encode(), socketAddress)

    while True:
        text = input()
        body = {'message': text, 'type': 'chat'}
        s.sendto(json.dumps(body).encode(), socketAddress)


t1 = threading.Thread(target=listen)
t2 = threading.Thread(target=handleInput)


t1.start()
t2.start()

t1.join()
t2.join()
