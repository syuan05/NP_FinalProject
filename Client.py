import os
import socket
import tkinter as tk
from tkinter import ttk, messagebox
import struct

USER_FILE = "users.txt"
BUFF: int = 1024

class GuessNumberClient:
    def __init__(self, root:tk.Tk ):
        self.root = root
        self.root.title("1A2B")
        self.root.geometry("600x600")
        self.server_ip: str = '127.0.0.1'
        self.port: int = 54321
        self.client_socket: socket.socket | None = None
        self.username: str|None = None
        self.msg: str|None = None
        self.mode: int = 0   # 0 login 1 register
        self.isLogin: bool = False
        self.isRegister: bool = False
        self.login_window()
        

    def login_window(self):
        tk.Label(self.root, text="Username:").pack(pady=5)
        self.username_input = tk.Entry(self.root)
        self.username_input.pack(pady=5)
        tk.Label(self.root, text="Password:").pack(pady=5)
        self.password_input = tk.Entry(self.root, show="*")
        self.password_input.pack(pady=5)
        tk.Button(self.root, text="Login", command=self.login).pack(pady=5)
        tk.Button(self.root, text="Register", command=self.register).pack(pady=5)
    
    def login(self):
        self.mode = 0
        self.username = self.username_input.get()
        password = self.password_input.get()
        username_len = len(self.username)
        password_len = len(password)

        if not self.username or not password:
            messagebox.showwarning("Input Error", "Please fill the username or password.")
            return
        
        # 封包
        data: bytes = struct.pack(f"!iII{username_len}s{password_len}s",self.mode,username_len,password_len,self.username.encode('utf-8'),password.encode("utf-8"))
        self.clear_window()
        self.connect_server(data)
        if self.isLogin and self.username:
            self.mode_ui()  #進到選擇模式UI
            self.msg = None
        if not self.isLogin and self.msg:
            messagebox.showerror("Error", self.msg)
            self.login_window()  
            self.msg = None

    def register(self):
        self.mode = 1 
        username = self.username_input.get()
        password = self.password_input.get()
        username_len = len(username)
        password_len = len(password)

        if not username or not password:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return
        
        data: bytes = struct.pack(f"!iII{username_len}s{password_len}s",self.mode,username_len,password_len,username.encode('utf-8'),password.encode("utf-8"))
        self.clear_window()
        self.connect_server(data)
        if self.isRegister:
            messagebox.showinfo("Success", "Registration successful! You can now log in.")
            self.login_window()
            self.isRegister = False
            self.msg = None
        elif not self.isRegister and self.msg:
            messagebox.showerror("Error", self.msg)
            self.login_window()
            self.msg = None   

    def mode_ui(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 創建單機模式按鈕
        self.single_button = tk.Button(self.main_frame, text="單機模式", command=self.single_create_ui)
        self.single_button.pack(pady=10)

        # 創建雙人模式按鈕
        self.multi_player_button = tk.Button(self.main_frame, text="雙人模式", command=self.wait_for_challenger)
        self.multi_player_button.pack(pady=10)

        
    def single_create_ui(self):
        self.clear_window()
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.left_frame = tk.Frame(self.main_frame, width=300, relief=tk.SUNKEN, borderwidth=1)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.left_frame.pack_propagate(False)
        self.show_history = ttk.Treeview(self.left_frame, columns=('Player', 'Guess', 'Result'), show='headings')
        self.show_history.heading('Player', text='Player')
        self.show_history.heading('Guess', text='Guess')
        self.show_history.heading('Result', text='Result')
        self.show_history.column('Player', width=100, anchor='center')
        self.show_history.column('Guess', width=100, anchor='center')
        self.show_history.column('Result', width=100, anchor='center')
        self.show_history.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.history_scrollbar = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.show_history.yview)
        self.show_history.configure(yscrollcommand=self.history_scrollbar.set)
        self.history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.right_frame = tk.Frame(self.main_frame, width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))
        self.right_frame.pack_propagate(False)

        self.title_label = tk.Label(self.main_frame, text="1A2B", font=('Arial', 16))
        self.title_label.pack(padx=10)

        self.input_frame = tk.Frame(self.right_frame)
        self.input_frame.pack(pady=5)

        self.guess_label = tk.Label(self.input_frame, text="Enter a number")
        self.guess_label.pack(side=tk.LEFT, padx=5)

        self.guess_input = tk.Entry(self.input_frame, width=10, font=('Arial', 12))
        self.guess_input.pack(side=tk.LEFT, padx=5)
        self.guess_input.bind('<Return>', self.send_guess)

        self.send_button = tk.Button(self.input_frame, text='Send', command=self.send_guess)
        self.send_button.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(self.right_frame, text="", font=('Arial', 10))
        self.status_label.pack(pady=10)
        
    def multi_create_ui(self):
        self.clear_window()
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.left_frame = tk.Frame(self.main_frame, width=300, relief=tk.SUNKEN, borderwidth=1)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.left_frame.pack_propagate(False)
        
        self.show_history = ttk.Treeview(self.left_frame, columns=('Player', 'Guess', 'Result'), show='headings')
        self.show_history.heading('Player', text='Player')
        self.show_history.heading('Guess', text='Guess')
        self.show_history.heading('Result', text='Result')
        self.show_history.column('Player', width=100, anchor='center')
        self.show_history.column('Guess', width=100, anchor='center')
        self.show_history.column('Result', width=100, anchor='center')
        self.show_history.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.history_scrollbar = ttk.Scrollbar(self.left_frame, orient=tk.VERTICAL, command=self.show_history.yview)
        self.show_history.configure(yscrollcommand=self.history_scrollbar.set)
        self.history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.right_frame = tk.Frame(self.main_frame, width=300)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5,0))
        self.right_frame.pack_propagate(False)

        self.title_label = tk.Label(self.main_frame, text="1A2B - Multiplayer Mode", font=('Arial', 16))
        self.title_label.pack(padx=10)

        self.input_frame = tk.Frame(self.right_frame)
        self.input_frame.pack(pady=5)

        self.guess_label = tk.Label(self.input_frame, text="Enter a number")
        self.guess_label.pack(side=tk.LEFT, padx=5)

        self.guess_input = tk.Entry(self.input_frame, width=10, font=('Arial', 12))
        self.guess_input.pack(side=tk.LEFT, padx=5)
        self.guess_input.bind('<Return>', self.send_guess)

        self.send_button = tk.Button(self.input_frame, text='Send', command=self.send_guess)
        self.send_button.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(self.right_frame, text="", font=('Arial', 10))
        self.status_label.pack(pady=10)


    def wait_for_challenger(self):
        self.main_frame.pack_forget()
        
        waiting_label = tk.Label(self.root, text="等待對手連線...")
        waiting_label.pack(pady=20)
        
        #啟動伺服器並處理連線
        #連到後要幹嘛
    
    def send_guess(self, event=None):
        self.msg = None
        try:
            guess = self.guess_input.get()
            if not guess.isdigit() or len(guess) != 4:
                messagebox.showwarning("Error input", "Please enter a 4-digit number")
                return
            self.client_socket.sendall(guess.encode('utf-8'))
            self.receive_message()
            self.guess_input.delete(0, tk.END)      # Clear input
        except Exception as e:
            self.status_label.config(text=f"Send error: {e}", fg="red")
            self.disconnect()
    
    def update_history(self, player, guess, result):
        self.root.after(0, lambda: self.show_history.insert('', 'end', values=(player, guess, result)))
        
    def connect_server(self, wantSend: bytes):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, self.port))
            self.client_socket.sendall(wantSend)
            self.receive_message()
            
        except Exception as e:
            messagebox.showerror("Connection error", str(e))
            self.root.quit()
            
    def receive_message(self):
        while self.msg is None:
            try:
                feedback = self.client_socket.recv(BUFF).decode('utf-8')
                print(f"Received message: {feedback}")
                
                if feedback == "Login Success":
                    self.isLogin = True
                if feedback == "Register successed":
                    self.isRegister = True
                if "guessed the correct number" in feedback:    
                    parts = feedback.split("|")
                    player = parts[0].split(" ")[0] 
                    ans = parts[1] if len(parts) > 1 else "Unknown"
                    self.status_label.config(text=f"Game Over! {parts[0]}", fg="blue")
                    self.guess_input.config(state=tk.DISABLED)
                    self.send_button.config(state=tk.DISABLED)
                    messagebox.showinfo("Game Over", f"The correct number was: {ans}")
                    
                elif "guess:" in feedback:
                    parts = feedback.split("|")
                    guess_info = parts[0] 
                    result = parts[1] if len(parts) > 1 else "Unknown"
                    player = guess_info.split(" ")[0]
                    guess = guess_info.split(": ")[1]
                    self.update_history(player, guess, result)
                self.msg = feedback
            except socket.timeout:
                self.status_label.config(text="Connection timed out, please try again.", fg="red")
                break
            except Exception as e:
                self.status_label.config(text=f"Receive error: {e}", fg="red")
                break
    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    
    def disconnect(self):
        if self.client_socket:
            self.client_socket.close()
        self.root.quit()
def main():
    root: tk.Tk = tk.Tk()
    client = GuessNumberClient(root)
    root.mainloop()

if __name__ == '__main__':
    main()