import socket


def main():
    # AF_INET stands for ipv4 address family
    # SOCK_STREAM stands for connection oriented socket (TCP)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socketAddr = ('127.0.0.1', 12345)

    s.connect(socketAddr)
    while True:
        chat = input("Enter the message to send to server or 0 to end connection : ")
        if chat == '0':
            return
        
        s.send(chat.encode())
        message = s.recv(1024).decode()
        if message != '':
            print('Server message recieved : {}'.format(message))


if __name__ == '__main__':
    main()
