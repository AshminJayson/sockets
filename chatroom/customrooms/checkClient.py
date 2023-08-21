import socket
import threading
import json
import random
import os
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketAddress = ('127.0.0.1', 12345)
s.bind(('', random.randint(1000, 10000)))  # Enable this on windows


username = 'Ash'
authorizationToken = 'd'

# payload = json.dumps(
#     {'username': username, 'AuthorizationToken': authorizationToken, 'chatroomName': 'dattebayo', 'chatroomPasskey': 'dattebayo', 'type': 'registration'}).encode()
# s.sendto(payload, socketAddress)

payload = json.dumps(
    {'message': 'Welcome to dattebayo', 'type': 'chat'}
)
s.sendto(payload, socketAddress)
