# Ashmin Jayson S7 DS 14
# Experiment 2 : Client Server communication using TCP
# Date : 18/8/23


import socket


def main():
    # AF_INET stands for ipv4 address family
    # SOCK_STREAM stands for connection oriented socket (TCP)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketAddr = ('127.0.0.1', 12345)

    s.bind(socketAddr)
    s.listen(5)

    print("Server listening on port: {}".format(socketAddr[1]))
    c, addr = s.accept()
    print(c, addr)
    while True:
        message = c.recv(1024).decode()
        print(message)
        reply = input("Enter reply to client or 0 : ")

        if reply == '0':
            c.close()
            return
        
        c.send(reply.encode())


if __name__ == "__main__":
    main()
