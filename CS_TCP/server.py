import socket


def main():
    # AF_INET stands for ipv4 address family
    # SOCK_STREAM stands for connection oriented socket (TCP)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketAddr = ('', 12345)

    s.bind(socketAddr)
    s.listen(5)

    print("Server listening on port: {}".format(socketAddr[1]))
    while True:
        c, addr = s.accept()
        print(c, addr)
        c.send("Dattebayo".encode())
        c.close()
        break


if __name__ == "__main__":
    main()
