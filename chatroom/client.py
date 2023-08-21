import socket
import threading
import json
import random
import os
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketAddress = ('127.0.0.1', 12345)
s.bind(('', random.randint(1000, 10000)))  # Enable this on windows


def listen():
    while True:
        message, address = s.recvfrom(1024)
        body = json.loads(message.decode())
        if body['type'] == 'notification':
            printToConsole(body['message'])
        else:
            printToConsole('{}: {}'.format(body['author'], body['message']))


def printToConsole(message):
    print(message)


def handleInput():
    try:
        print("-- Welcome to the chat room --")
        name = input("Username:")
        password = input("Server authorization passkey:")

        body = {
            'name': name,
            'password': password,
            'type': 'registration'
        }

        s.sendto(json.dumps(body).encode(), socketAddress)

        while True:
            text = input()
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K")
            print("-------------------------------- You:", text)
            body = {'message': text, 'type': 'chat'}
            s.sendto(json.dumps(body).encode(), socketAddress)
    except:
        print("\nException occured")
        os._exit(1)


t1 = threading.Thread(target=listen)
t2 = threading.Thread(target=handleInput)


t1.start()
t2.start()

t1.join()
t2.join()
