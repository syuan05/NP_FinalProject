import socket

serverIP = '127.0.0.1'
PORT = 54321

def main():
    cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Connecting to %s port %s' % (serverIP, PORT))
    cSocket.connect((serverIP, PORT))
    while True:
        guess = int(input("Enter a number(0000-9999): "))
        cSocket.send(str(guess).encode('utf-8'))
        feedback = cSocket.recv(1024).decode('utf-8')
        print(feedback)
        if 'correct' in feedback:
            break
    cSocket.close()

if __name__ == '__main__':
    main()
        