import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketAddress = ('127.0.0.1', 12345)

s.sendto(str.encode("Dattebayo"), socketAddress)

serverReply = s.recvfrom(1024)

print("Server reply : {}".format(serverReply[0].decode()))
