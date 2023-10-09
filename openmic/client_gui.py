import socket
import threading
import json
import random
import os
import sys
import time
import customtkinter
from collections import deque
from tkinter import *

q = deque()

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.settimeout(1)
socketAddress = ('127.0.0.1', 12345)
s.bind(('', random.randint(1000, 10000)))  # Enable this on windows



app = customtkinter.CTk()
app.geometry("400x240")

app.title("Open Mic")

customtkinter.set_appearance_mode("System") 
customtkinter.set_default_color_theme("blue")

login_frame = customtkinter.CTkFrame(master=app)
login_frame.pack(fill="both", expand=True)


chat_frame = customtkinter.CTkFrame(master=app)
messages = customtkinter.CTkTextbox(master=chat_frame)
typing_area = customtkinter.CTkEntry(master=chat_frame, placeholder_text="Enter message")

def switch_to_chat():
    q.append([login_frame, 2])
    q.append([chat_frame, 1])
    q.append([messages, 1])
    q.append([typing_area, 1])
    q.append([send, 1])


username = customtkinter.CTkEntry(master=login_frame, placeholder_text="Username")
username.pack()
server_auth_token = customtkinter.CTkEntry(master=login_frame, placeholder_text="Server Authorization Token")
server_auth_token.pack()


t1 = None
t2 = None


def initialize_client():

    username_value = username.get()
    server_auth_token_value = server_auth_token.get()

    print("Enter q() to exit the chatroom")

    body = {
        'name': username_value,
        'password': server_auth_token_value,
        'type': 'registration'
    }

    s.sendto(json.dumps(body).encode(), socketAddress)

def handleInput():
    text = typing_area.get()
    try:
        def reverse_phrase(phrase):
            phrase = [*phrase]
            return ''.join(phrase[::-1])

        if text == 'q()': signalTerminate()
        sys.stdout.write("\033[F")
        sys.stdout.write("\033[K")

        text = reverse_phrase(text)
        
        print("-------------------------------- You:", text)
        body = {'message': text, 'type': 'chat'}
        s.sendto(json.dumps(body).encode(), socketAddress)
    except:
        print("\nException occured")
        signalTerminate()


button = customtkinter.CTkButton(master=login_frame, text="Initialize Client", command=initialize_client)
send = customtkinter.CTkButton(master=chat_frame, text='Send', command=handleInput)
button.pack()

def printToConsole(message):
    messages.insert("0.0", message + '\n')

def signalTerminate():
    print('Terminating client...')
    s.close()
    os._exit(1)


def listen():
    message, address = None, None
    try:
        message, address = s.recvfrom(1024)
    except:
        pass
    finally:
        app.after(3000, listen)

    if not message: return
    body = json.loads(message.decode())
    if body['type'] == 'notification':
        print(body['message'])
        if body['message'] == 'Login Successfull':
            switch_to_chat()
        elif body['message'] == 'Invalid password':
            signalTerminate()


        printToConsole(body['message'])
        # if body['message'] == 'Invalid password':
            # signalTerminate()
    else:
        printToConsole('{}: {}'.format(body['author'], body['message']))






def swithcher():
    while q:
        data, operation = q.popleft()
        if operation == 1:
            data.pack()
        elif operation == 2:
            data.destroy()
    app.after(1000, swithcher)



app.after(1000, swithcher)
app.after(5000, listen)
app.mainloop()


