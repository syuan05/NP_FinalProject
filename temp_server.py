from io import TextIOWrapper
import os
import random
import socket
import threading
import struct
BUFF = 1024
class GameServer(threading.Thread):
    def __init__(self, client: socket.socket, rip: str,rport:int,username: str):
        super().__init__()
        self.ans: list[int] = [random.randrange(10) for _ in range(4)]
        self.client = client
        self.rip = rip
        self.rport = rport
        self.username = username
        self.start()
        
    def run(self):
        # 接收帳號名稱
        port = self.rport
        addr = f"{self.rip}:{self.rport}"
        while True:
            try:
                receive = self.client.recv(BUFF).decode('utf-8')
                print("receive: ",receive)
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
                    msg = f"{self.username} guessed the correct number!|Ans: {self.ans}"
                    # self.broadcast(msg, client)
                    self.client.sendall(msg.encode('utf-8'))
                    break
                else:
                    msg = f"{self.username} guess: {guess}|A:{ACount} B:{BCount}"
                    print(msg)
                    # self.broadcast(msg, client)
                    self.client.sendall(msg.encode('utf-8'))
            except Exception as e:
                print(f"Error: {e}")
                break
        self.client.close()
class Main:
    def __init__(self, host:str ='', port: int=54321):
        self.host = host
        self.port = port
        self.srv_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.srv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    def start(self):
        self.srv_socket.bind((self.host, self.port))
        self.srv_socket.listen(5)
        while True:
            print("Waiting for connect...")
            client, (rip,rport) = self.srv_socket.accept()
            auth_thread = AuthThread("AuthThread",True,client,rip,rport)
            print(f"{rip}:{rport} has connected.")
    def close(self):
            self.srv_socket.close()
    
            
class AuthThread(threading.Thread):
    def __init__(self,t_name: str, deamon: bool,client_sc: socket.socket,rip: str,rport: int):
        super().__init__(name=t_name,daemon=deamon)
        self.client: socket.socket = client_sc
        self.rip: str = rip
        self.rport: int = rport
        self.username: str = None
        self.password: str = None
        self.isLogin: bool = False
        self.mode: int = 0
        self.UserFile: str = "users.txt"
        self.file: TextIOWrapper = None
        self.start()
    def run(self):
        msg: bytes = self.client.recv(BUFF)
        self.UserInfoPaser(msg)
        match self.mode:
            case 0:
                self.login()
            case 1:
                self.register()
    def login(self):
        self.getUserData_handler("r")
        msg: str|None = None
        if self.file is None:
            msg = "No users found. Please register first.".encode('utf-8')
        else:
            for line in self.file:
                stored_username, stored_password = line.strip().split("|")
                if self.username == stored_username and self.password == stored_password:
                    msg = f"Login Success".encode('utf-8')
                    break
            else:
                msg = "Username or Password have Error".encode('utf-8')
        if msg:
            self.client.sendall(msg)
        self.closeUserData_handler()
        game = GameServer(self.client, self.rip,self.rport,self.username)
        print(f"Ans: {game.ans}")
    def register(self):
        msg: str = None
        self.getUserData_handler("r",True)
        for line in self.file:
            stored_username, _ = line.strip().split("|")
            if self.username == stored_username:
                msg = "Username already exists.".encode('utf-8')
            break
        else:
            msg = "Register successed".encode('utf-8')
        if msg:
            self.client.sendall(msg)
        self.getUserData_handler('w+',True)
        self.file.writelines(f"{self.username}|{self.password}")
        self.closeUserData_handler()
        
    def UserInfoPaser(self,form: bytes):
        header_format = "!iII"
        header_size = struct.calcsize(header_format)
        self.mode, username_len, password_len = struct.unpack(header_format,form[:header_size])
        userInfo_format = f"{username_len}s{password_len}s"
        username_bytes, password_bytes = struct.unpack(userInfo_format,form[header_size:])
        self.username: str = username_bytes.decode('utf-8')
        self.password: str = password_bytes.decode('utf-8')
    def getUserData_handler(self,mode: str,CanCreate: bool = False):
        if self.file:
            self.file.close()
        if CanCreate:
            if not os.path.exists(self.UserFile):
                open(self.UserFile,'w').close()
        try:
            self.file = open(self.UserFile,mode)
        except FileNotFoundError:
            self.file = None
    def closeUserData_handler(self):
        if self.file:
            self.file.close()
                    
    
            
if __name__ == '__main__':
    mainThread = Main()
    try:
        mainThread.start()
    except KeyboardInterrupt:
        print("Server close")
        mainThread.close()
