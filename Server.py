import random
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

current_player = None
serverIP = '127.0.0.1'
PORT = 54321
ans = [random.randrange(10) for _ in range(4)]

clients = []
clients_lock = threading.Lock()

def broadcast(message, sender_client=None):
    print(f"Broadcasting message: {message}")
    with clients_lock:
        for client in clients:
            if client != sender_client:
                try:
                    client.sendall(message.encode('utf-8'))
                except:
                    clients.remove(client)
                
def game_start(client, addr):
    port = addr[1]
    with clients_lock:
        clients.append(client)
    while True:
        try:
            receive = client.recv(1024).decode('utf-8')
            num = int(receive)
            guess = [0] * 4
            digit = 1000
            ACount = 0
            BCount = 0
            guess_used = [False] * 4
            ans_used = [False] * 4
            print(f"Receive {num} from {addr}")
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
                msg = f"{port} guessed the correct number!|Ans: {ans}"  # 用 | 分隔
                broadcast(msg, client)
                client.sendall(msg.encode('utf-8'))
                break
            else:
                msg = f"{port} guess: {guess}|A:{ACount} B:{BCount}"
                broadcast(msg, client)
                client.sendall(msg.encode('utf-8'))
        except Exception as e:
            print(f"Error: {e}")
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