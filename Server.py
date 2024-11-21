import random
import socket
import threading

serverIP = '127.0.0.1'
PORT = 54321

def game_start(client, add):
    ans = [random.randrange(10) for _ in range(4)]
    while True:
        receive = client.recv(1024)
        num = int(receive)
        guess = [0] * 4
        digit = 1000
        ACount = 0
        BCount = 0
        ans_used = [False] * 4
        print(f"Receive {num}")
        for i in range(4):
            guess[i] = num // digit
            num %= digit
            digit //= 10
        for i in range(4):
            if guess[i] == ans[i]:
                ACount += 1
                ans_used[i] = True

        for i in range(4):
            for j in range(4):
                if guess[i] == ans[j] and i != j and not ans_used[i]:
                    BCount += 1
                    ans_used[j] = True
        client.sendall(f"your guess: {guess} \nA:{ACount} B:{BCount}".encode('utf-8'))
        if ACount == 4:
            client.sendall("You guess the correct number!".encode('utf-8'))
            break
    client.close()

def main():
    srvSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srvSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print('Waiting to recive a number from client')
    srvSocket.bind(('', PORT))
    srvSocket.listen(5)
    while True:
        client, add = srvSocket.accept()
        client_thread = threading.Thread(target=game_start, args=(client, add))
        client_thread.start()

if __name__ == '__main__':
    main()