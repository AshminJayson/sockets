import socket

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
socketAddress = ('127.0.0.1', 12345)


while True:
    snd = input("Enter message to send to server or 0 to close chat: ")
    if snd == '0': break
    s.sendto(snd.encode(), socketAddress)


    serverReply = s.recvfrom(1024)
    if serverReply != '':
        print("Server reply : {}".format(serverReply[0].decode()))
