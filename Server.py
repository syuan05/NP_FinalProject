import random
import socket
import threading

class GameServer:
    def __init__(self, host='127.0.0.1', port=54321):
        self.server_ip = host
        self.port = port
        self.clients = []
        self.clients_lock = threading.Lock()
        self.ans = [random.randrange(10) for _ in range(4)]
        self.srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def broadcast(self, message, sender_client=None):
        print(f"Broadcasting message: {message}")
        with self.clients_lock:
            for client in self.clients:
                if client != sender_client:
                    try:
                        client.sendall(message.encode('utf-8'))
                    except:
                        self.clients.remove(client)

    def game_start(self, client, addr):
        port = addr[1]
        with self.clients_lock:
            self.clients.append(client)

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
                    if guess[i] == self.ans[i]:
                        ACount += 1
                        ans_used[i] = True
                        guess_used[i] = True

                for i in range(4):
                    if not guess_used[i]:
                        for j in range(4):
                            if guess[i] == self.ans[j] and not ans_used[j]:
                                BCount += 1
                                ans_used[j] = True
                                break

                if ACount == 4:
                    msg = f"{port} guessed the correct number!|Ans: {self.ans}"
                    self.broadcast(msg, client)
                    client.sendall(msg.encode('utf-8'))
                    break
                else:
                    msg = f"{port} guess: {guess}|A:{ACount} B:{BCount}"
                    self.broadcast(msg, client)
                    client.sendall(msg.encode('utf-8'))
            except Exception as e:
                print(f"Error: {e}")
                break
        client.close()

    def start(self):
        self.srv_socket.bind(('', self.port))
        self.srv_socket.listen(5)
        while True:
            print("Waiting for connect...")
            client, add = self.srv_socket.accept()
            client_thread = threading.Thread(target=self.game_start, args=(client, add))
            client_thread.start()
            print(f"{add} has connected.")
            
if __name__ == '__main__':
    server = GameServer()
    server.start()
