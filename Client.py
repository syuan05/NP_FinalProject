import os
import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox

USER_FILE = "users.txt"

class GuessNumberClient:
    def __init__(self, root):
        self.root = root
        self.root.title("1A2B")
        self.root.geometry("600x600")
        
        self.server_ip = '127.0.0.1'
        self.port = 54321
        self.client_socket = None
        self.username = None

        self.login_window()

    def login_window(self):
        # self.login_win = tk.Toplevel(self.root)
        # self.login_win.title("Login/Register")
        
        tk.Label(self.root, text="Username:").pack(pady=5)
        self.username_input = tk.Entry(self.root)
        self.username_input.pack(pady=5)

        tk.Label(self.root, text="Password:").pack(pady=5)
        self.password_input = tk.Entry(self.root, show="*")
        self.password_input.pack(pady=5)

        tk.Button(self.root, text="Login", command=self.login).pack(pady=5)
        tk.Button(self.root, text="Register", command=self.register).pack(pady=5)
    
    def login(self):
        username = self.username_input.get()
        password = self.password_input.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please fill the username or password.")
            return
        if not os.path.exists(USER_FILE):
            messagebox.showerror("Error", "No users found. Please register first.")
            return
        
        with open(USER_FILE, "r") as file:
            for line in file:
                stored_username, stored_password = line.strip().split("|")
                if username == stored_username and password == stored_password:
                    self.username = username
                    messagebox.showinfo("Success", "Login successful!")
                    self.clear_window()
                    self.connect_server()
                    self.create_ui()
                    return

        messagebox.showerror("Error", "Invalid username or password.")

    def register(self):
        username = self.username_input.get()
        password = self.password_input.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        if os.path.exists(USER_FILE):
            with open(USER_FILE, "r") as file:
                for line in file:
                    stored_username, _ = line.strip().split("|")
                    if username == stored_username:
                        messagebox.showerror("Error", "Username already exists.")
                        return

        with open(USER_FILE, "a") as file:
            file.write(f"{username}|{password}\n")
        
        messagebox.showinfo("Success", "Registration successful! You can now log in.")

    def create_ui(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.left_frame = tk.Frame(self.main_frame, width=300, relief=tk.SUNKEN, borderwidth=1)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.left_frame.pack_propagate(False)

        # View history
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
        # self.game_log = tk.Text(self.root, wrap=tk.WORD, width=50, height=15)
        # self.game_log.pack(padx=10, pady=10)
    
    def send_guess(self, event=None):
        try:
            guess = self.guess_input.get()

            if not guess.isdigit() or len(guess) != 4:
                messagebox.showwarning("Error input", "Please enter a 4-digit number")
                return
            
            self.client_socket.send(guess.encode('utf-8'))
            self.guess_input.delete(0, tk.END)      # Clear input
        except Exception as e:
            self.status_label.config(text=f"Send error: {e}", fg="red")
            self.disconnect()
    
    def update_history(self, player, guess, result):
        self.root.after(0, lambda: self.show_history.insert('', 'end', values=(player, guess, result)))
    def connect_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, self.port))
            self.receive_thread = threading.Thread(target=self.receive_message)
            self.receive_thread.daemon = True
            self.receive_thread.start()
        except Exception as e:
            messagebox.showerror("Connection error", str(e))
            self.root.quit()
    def receive_message(self):
        while True:
            try:
                feedback = self.client_socket.recv(1024).decode('utf-8')
                print(f"Received message: {feedback}")
                if "It's not your turn" in feedback:
                    self.guess_input.config(state=tk.DISABLED)
                    self.status_label.config(text="It's not your turn. Please wait.", fg="red")
                elif "Your turn" in feedback:
                    self.guess_input.config(state=tk.NORMAL)
                    self.status_label.config(text="It's your turn. Please make a guess.", fg="green")
                if "guessed the correct number" in feedback:    
                    parts = feedback.split("|")
                    player = parts[0].split(" ")[0] 
                    ans = parts[1] if len(parts) > 1 else "Unknown"
                    self.status_label.config(text=f"Game Over! {parts[0]}", fg="blue")
                    self.guess_input.config(state=tk.DISABLED)
                    self.send_button.config(state=tk.DISABLED)
                    messagebox.showinfo("Game Over", f"The correct number was: {ans}")
                    break
                
                elif "guess:" in feedback:
                    parts = feedback.split("|")
                    guess_info = parts[0] 
                    result = parts[1] if len(parts) > 1 else "Unknown"
                    player = guess_info.split(" ")[0]
                    guess = guess_info.split(": ")[1]
                    self.update_history(player, guess, result)
                
                else:
                    self.status_label.config(text=feedback, fg="black")
            
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
    root = tk.Tk()
    client = GuessNumberClient(root)
    root.mainloop()

if __name__ == '__main__':
    main()
        