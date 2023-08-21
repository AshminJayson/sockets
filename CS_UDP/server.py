import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host = socket.gethostname()
socketAddr = ('127.0.0.1', 12345)

print(host)

s.bind(socketAddr)

print("Server listening on port {}".format(socketAddr[1]))

while True:
    message, address = s.recvfrom(1024)
    print("Got message {} from {}".format(message.decode(), address))

    response = str.encode(input("Enter the response to client or 0:"))
    if response == '0':
        break
    s.sendto(response, address)


