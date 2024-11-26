import random
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

serverIP = '127.0.0.1'
PORT = 54321
ans = [random.randrange(10) for _ in range(4)]

clients = []
clients_lock = threading.Lock()

def broadcast(message, sender_client=None):
    with clients_lock:
        for client in clients:
            if clients != sender_client:
                try:
                    client.sendall(message).encode('utf-8')
                except:
                    clients.remove(client)
                
def game_start(client, addr):
    with clients_lock:
        clients.append(client)
    while True:
        receive = client.recv(1024)
        num = int(receive)
        guess = [0] * 4
        digit = 1000
        ACount = 0
        BCount = 0
        guess_used = [False] * 4
        ans_used = [False] * 4
        print(f"Receive {num}")
        if num == 1:
            print(f"{ans}\ngame end")
        for i in range(4):
            guess[i] = num // digit
            num %= digit
            digit //= 10
        for i in range(4):
            if guess[i] == ans[i]:
                ACount += 1
                ans_used[i] = True
                guess_used[i] = True

        for i in range(4):
            if not guess_used[i]:
                for j in range(4):
                    if guess[i] == ans[j] and not ans_used[j]:
                        BCount += 1
                        ans_used[j] = True
                        break
        if ACount == 4:
            msg = f"{addr} guess the correct number!\nAns: {ans}"
            broadcast(msg, client)
            client.sendall(f"You guess the correct number!".encode('utf-8'))
            break
        else:
            msg = f"{addr} guess: {guess} \nA:{ACount} B:{BCount}"
            broadcast(msg, client)
            client.sendall(f"your guess: {guess} \nA:{ACount} B:{BCount}".encode('utf-8'))
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