import os
import random
import socket
import threading

USER_FILE = "users.txt"

class GameServer:
    def __init__(self, host='127.0.0.1', port=54321):
        self.server_ip = host
        self.port = port
        self.clients = []
        self.clients_lock = threading.Lock()
        self.ans = [random.randrange(10) for _ in range(4)]
        self.srv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.logged_in_users = set()
        
        self.current_turn_index = 0
        self.game_players = []
        self.game_in_progress = False
        self.online_players = []

    def broadcast(self, message, sender_client=None):
        print(f"Broadcasting message: {message}")
        with self.clients_lock:
            for client in self.clients:
                if client != sender_client:
                    try:
                        client.sendall(message.encode('utf-8'))
                    except:
                        self.clients.remove(client)

    def send_online_players(self, client):
        online_players_str = "|".join(self.online_players)
        client.sendall(f"ONLINE_PLAYERS|{online_players_str}".encode('utf-8'))

    def handle_login(self, client):
        try:
            while True:
                data = client.recv(1024).decode('utf-8')
                if not data:
                    break
                
                command, username, password = data.split("|")

                if command == "REGISTER":
                    if self.register_user(username, password):
                        client.sendall("REGISTER_SUCCESS|Registration successful!".encode('utf-8'))
                    else:
                        client.sendall("REGISTER_FAILED|Username already exists.".encode('utf-8'))

                elif command == "LOGIN":
                    if username in self.logged_in_users:
                        client.sendall("LOGIN_FAILED|User is already logged in.".encode('utf-8'))
                    elif self.validate_login(username, password):
                        self.logged_in_users.add(username)
                        client.sendall("LOGIN_SUCCESS|Login successful!".encode('utf-8'))
                        return username
                    else:
                        client.sendall("LOGIN_FAILED|Invalid username or password.".encode('utf-8'))
                else:
                    client.sendall("ERROR|Unknown command.".encode('utf-8'))
        except Exception as e:
            print(f"Login/Register error: {e}")
        return None

    def register_user(self, username, password):
        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r") as file:
                for line in file:
                    stored_username, _ = line.strip().split("|")
                    if username == stored_username:
                        return False 

        with open(USER_FILE, "a") as file:
            file.write(f"{username}|{password}\n")
        return True

    def validate_login(self, username, password):
        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r") as file:
                for line in file:
                    stored_username, stored_password = line.strip().split("|")
                    if username == stored_username and password == stored_password:
                        return True 
        return False

    def start_game(self):
        self.ans = [random.randrange(10) for _ in range(4)]
        self.current_turn_index = 0
        self.game_in_progress = True
        
        # start_message = f"Game Started! Number chosen. {self.game_players[self.current_turn_index].username}'s turn."
        # for player in self.game_players:
            # player.client.sendall(start_message.encode('utf-8'))
        
        first_player = self.game_players[self.current_turn_index]
        first_player.client.sendall("Your turn|Please make a guess.".encode('utf-8'))

    def next_turn(self):
        self.current_turn_index = (self.current_turn_index + 1) % len(self.game_players)
        
        for player in self.game_players:
            if player.client == self.game_players[self.current_turn_index].client:
                player.client.sendall("Your turn|Please make a guess.".encode('utf-8'))
            else:
                player.client.sendall(f"It's {self.game_players[self.current_turn_index].username}'s turn.".encode('utf-8'))

    def game_start(self, client, addr):
        username = self.handle_login(client)
        if not username:
            print(f"Client {addr} failed to log in.")
            client.close()
            return
        
        print(f"User '{username}' from {addr} has logged in.")
        
        self.online_players.append(username)
        self.send_online_players(client)
        online_players_str = "|".join(self.online_players)
        self.broadcast(f"ONLINE_PLAYERS|{online_players_str}")
        
        class Player:
            def __init__(self, client, username):
                self.client = client
                self.username = username
        
        player = Player(client, username)
        
        with self.clients_lock:
            self.clients.append(client)
            self.game_players.append(player)
        
        if len(self.game_players) >= 2 and not self.game_in_progress:
            print(f"Starting game with {len(self.game_players)} players")
            self.start_game()

        while True:
            try:
                receive = client.recv(1024).decode('utf-8')
                if not receive:
                    break
                
                if client != self.game_players[self.current_turn_index].client:
                    client.sendall("It's not your turn.".encode('utf-8'))
                    continue
                
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
                    msg = f"{username} guessed the correct number!|Ans: {self.ans}"
                    self.broadcast(msg, client)
                    client.sendall(msg.encode('utf-8'))
                    break
                else:
                    msg = f"{username} guess: {guess}|A:{ACount} B:{BCount}"
                    self.broadcast(msg, client)
                    client.sendall(msg.encode('utf-8'))
                    self.next_turn()
            except Exception as e:
                print(f"Error: {e}")
                break
        
        self.online_players.remove(username)
        online_players_str = "|".join(self.online_players)
        self.broadcast(f"ONLINE_PLAYERS|{online_players_str}")
        
        client.close()

    def start(self):
        self.srv_socket.bind(('', self.port))
        self.srv_socket.listen(5)
        print("Server started. Waiting for connections...")

        while True:
            client, addr = self.srv_socket.accept()
            print(f"{addr} has connected.")
            client_thread = threading.Thread(target=self.game_start, args=(client, addr))
            client_thread.start()
            
if __name__ == '__main__':
    server = GameServer()
    server.start()