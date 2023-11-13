import socket
import threading
import json
import random
import os
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketAddress = ('127.0.0.1', 12345)
s.bind(('', random.randint(1000, 10000)))  # Enable this on windows


def printToConsole(message):
    print(message)

def signalTerminate():
    print('Terminating client...')
    s.close()
    os._exit(1)


def listen():
    while True:
        message, address = s.recvfrom(1024)
        body = json.loads(message.decode())
        if body['type'] == 'notification':
            printToConsole(body['message'])
            # if body['message'] == 'Invalid password':
                # signalTerminate()
        else:
            printToConsole('{}: {}'.format(body['author'], body['message']))


def handleInput():
    try:
        print("-- Welcome to the chat room --")
        name = input("Username:")
        password = input("Server authorization passkey:")
        print("Enter q() to exit the chatroom")

        body = {
            'name': name,
            'password': password,
            'type': 'registration'
        }

        s.sendto(json.dumps(body).encode(), socketAddress)

        while True:
            text = input()
            if text == 'q()': signalTerminate()
            sys.stdout.write("\033[F")
            sys.stdout.write("\033[K")
            print("-------------------------------- You:", text)
            body = {'message': text, 'type': 'chat'}
            s.sendto(json.dumps(body).encode(), socketAddress)
    except:
        print("\nException occured")
        signalTerminate()


t1 = threading.Thread(target=listen)
t2 = threading.Thread(target=handleInput)


t1.start()
t2.start()

t1.join()
t2.join()
