import socket


def main():
    # AF_INET stands for ipv4 address family
    # SOCK_STREAM stands for connection oriented socket (TCP)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketAddr = ('127.0.0.1', 12345)

    try:
        s.connect(socketAddr)
        message = s.recv(1024).decode()
        print('Server message recieved : {}'.format(message))
    except:
        print("Invalid socket address")


if __name__ == '__main__':
    main()
