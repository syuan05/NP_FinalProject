import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox

class GuessNumberClient:
    def __init__(self, root):
        self.root = root
        self.root.title("1A2B")
        self.root.geometry("600x600")

        self.server_ip = '127.0.0.1'
        self.port = 54321
        self.client_socket = None
        self.username = None
        self.is_my_turn = False

        self.create_login_window()

    def create_login_window(self):
        tk.Label(self.root, text="Username:").pack(pady=5)
        self.username_input = tk.Entry(self.root)
        self.username_input.pack(pady=5)

        tk.Label(self.root, text="Password:").pack(pady=5)
        self.password_input = tk.Entry(self.root, show="*")
        self.password_input.pack(pady=5)

        tk.Button(self.root, text="Login", command=self.login).pack(pady=5)
        tk.Button(self.root, text="Register", command=self.register).pack(pady=5)

        self.root.bind('<Return>', lambda event: self.safe_login())

    def safe_login(self):
        try:
            self.login()
        except AttributeError:
            messagebox.showerror("Error", "Login window is not active.")


    def connect_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, self.port))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to server: {e}")
            self.root.quit()

    def login(self):
        if not hasattr(self, 'username_input') or not hasattr(self, 'password_input'):
            messagebox.showerror("Error", "Input fields are not available.")
            return

        username = self.username_input.get()
        password = self.password_input.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        self.connect_server()
        self.client_socket.sendall(f"LOGIN|{username}|{password}".encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')

        if "LOGIN_SUCCESS" in response:
            self.username = username
            messagebox.showinfo("Success", "Login successful!")
            self.clear_window()
            self.create_game_ui()
            self.listen_server()
        elif "already logged in" in response:
            messagebox.showerror("Login Failed", "This user is already logged in!")
            self.clear_input_fields()
            self.client_socket.close()
        else:
            messagebox.showerror("Login Failed", response.split("|")[1])
            self.clear_input_fields()
            self.client_socket.close()


    def clear_input_fields(self):
        self.username_input.delete(0, tk.END)
        self.password_input.delete(0, tk.END)

    def register(self):
        username = self.username_input.get()
        password = self.password_input.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        self.connect_server()
        self.client_socket.sendall(f"REGISTER|{username}|{password}".encode('utf-8'))
        response = self.client_socket.recv(1024).decode('utf-8')

        if "REGISTER_SUCCESS" in response:
            messagebox.showinfo("Success", "Registration successful!")
        else:
            messagebox.showerror("Register Failed", response.split("|")[1])
        self.client_socket.close()

    def clear_window(self):
        self.root.unbind('<Return>')

        for widget in self.root.winfo_children():
            widget.destroy()

    def create_game_ui(self):
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
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
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

        self.status_label = tk.Label(self.right_frame, text="Waiting for game to start", font=('Arial', 10))
        self.status_label.pack(pady=10)

        self.online_players_label = tk.Label(self.right_frame, text="線上玩家：", font=('Arial', 10))
        self.online_players_label.pack(pady=5)

        self.quit_button = tk.Button(self.right_frame, text='Leave', command=self.disconnect)
        self.quit_button.pack(pady=10)

        self.guess_input.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)

    def send_guess(self, event=None):
        try:
            # 获取输入
            guess = self.guess_input.get()

            # 清空输入框并禁用控件，确保用户无法再次输入
            self.guess_input.delete(0, tk.END)
            self.guess_input.config(state=tk.DISABLED)
            self.send_button.config(state=tk.DISABLED)

            # 检查是否是该玩家的回合
            if not self.is_my_turn:
                messagebox.showwarning("Not Your Turn", "It's not your turn to guess!")
                return

            # 验证输入是否为4位数字
            if not guess.isdigit() or len(guess) != 4:
                messagebox.showwarning("Error input", "Please enter a 4-digit number")
                # 恢复输入框状态以便玩家重新输入
                self.guess_input.config(state=tk.NORMAL)
                self.send_button.config(state=tk.NORMAL)
                return

            # 发送猜测到服务器
            self.client_socket.send(guess.encode('utf-8'))

        except Exception as e:
            self.status_label.config(text=f"Send error: {e}", fg="red")
            self.disconnect()


    def update_history(self, player, guess, result):
        self.root.after(0, lambda: self.show_history.insert('', 'end', values=(player, guess, result)))

    def listen_server(self):
        self.receive_thread = threading.Thread(target=self.receive_message)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def receive_message(self):
        while True:
            try:
                feedback = self.client_socket.recv(1024).decode('utf-8')
                
                # 處理線上玩家更新
                if feedback.startswith("ONLINE_PLAYERS|"):
                    players = feedback.split("|")[1:]
                    players_text = "Online Player：" + ", ".join(players)
                    self.online_players_label.config(text=players_text)
                
                elif feedback.startswith("GAME_TERMINATED"):
                    self.status_label.config(text="Game terminated", fg="red")
                    self.guess_input.config(state=tk.DISABLED)
                    self.send_button.config(state=tk.DISABLED)
                    messagebox.showwarning("Game Over", "A player has disconnected. Game terminated.")
                    break
                elif "Game Started" in feedback:
                    self.status_label.config(text=feedback, fg="green")
                
                elif "Your turn" in feedback:
                    self.is_my_turn = True
                    self.guess_input.config(state=tk.NORMAL)
                    self.send_button.config(state=tk.NORMAL)
                    self.status_label.config(text="It's your turn. Please make a guess.", fg="green")
                
                elif "It's not your turn" in feedback:
                    self.is_my_turn = False
                    self.guess_input.config(state=tk.DISABLED)
                    self.send_button.config(state=tk.DISABLED)
                    self.status_label.config(text=feedback, fg="red")
                
                elif "guessed the correct number" in feedback:
                    parts = feedback.split("|")
                    self.status_label.config(text=f"Game Over! {parts[0]}", fg="blue")
                    self.guess_input.config(state=tk.DISABLED)
                    self.send_button.config(state=tk.DISABLED)
                    messagebox.showinfo("Game Over", f"The correct number was: {parts[1]}")
                    break
                
                elif "guess:" in feedback:
                    parts = feedback.split("|")
                    player = parts[0].split(" ")[0]
                    guess = parts[0].split(": ")[1]
                    result = parts[1]
                    self.update_history(player, guess, result)
                
                else:
                    self.status_label.config(text=feedback, fg="black")
            
            except Exception as e:
                self.status_label.config(text=f"Receive error: {e}", fg="red")
                messagebox.showerror("Connection Error", "Lost connection to server")
                break

    def disconnect(self):
        answer = messagebox.askyesno("Exit Game", "Are you sure you want to leave?")
        if answer: 
            if self.client_socket:
                self.client_socket.close()
            self.root.quit()
        else: 
            self.status_label.config(text="Welcome back to the game!", fg="blue")

def main():
    root = tk.Tk()
    client = GuessNumberClient(root)
    root.mainloop()

if __name__ == '__main__':
    main()