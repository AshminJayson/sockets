import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = socket.gethostname()
socketAddr = ('172.18.109.20', 12345)

print(host)

s.bind(socketAddr)

print("Server listening on port {}".format(socketAddr[1]))


clients = {}


def listen():
    while True:
        message, address = s.recvfrom(1024)
        msg = message.decode()

        if address in clients:
            print("Got message {} from {}".format(msg, clients[address]))
            sendMessage(msg, address)
        
        if address not in clients:
            clients[address] = msg
            sendMessage(msg + " joined the chat", address)


def sendMessage(msg, recAddress):
    recName = clients[recAddress]
    snd = msg + "^" + recName
    for clientAddress in list(clients.keys()):
        if clientAddress == recAddress: continue
        s.sendto(snd.encode(), clientAddress)

listen()


