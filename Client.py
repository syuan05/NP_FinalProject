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
        self.create_ui()
        self.connect_server()

    def create_ui(self):
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.left_frame = tk.Frame(self.main_frame, width=300, relief=tk.SUNKEN, borderwidth=1)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        self.left_frame.pack_propagate(False)

        # View history
        self.show_history = ttk.Treeview(self.left_frame, columns=('Guess', 'Result'), show='headings')
        self.show_history.heading('Guess', text='Guess')
        self.show_history.heading('Result', text='Result')
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
    
    def update_history(self, guess, result):
        self.root.after(0, lambda: self.show_history.insert('', 0, values=(guess, result)))
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
                
                if "guessed the correct number" in feedback:  # 游戏结束
                    parts = feedback.split("|")
                    ans = parts[1] if len(parts) > 1 else "Unknown"
                    self.status_label.config(text=f"Game Over! {parts[0]}", fg="blue")
                    self.guess_input.config(state=tk.DISABLED)
                    self.send_button.config(state=tk.DISABLED)
                    messagebox.showinfo("Game Over", f"The correct number was: {ans}")
                    break
                
                elif "guess:" in feedback:  # 普通猜测结果
                    parts = feedback.split("|")
                    guess_info = parts[0]  # 包括 addr 和 guess
                    result = parts[1] if len(parts) > 1 else "Unknown"
                    guess = guess_info.split(": ")[1]  # 提取 guess 值
                    self.update_history(guess, result)
                
                else:  # 未知消息
                    self.status_label.config(text=feedback, fg="black")
            
            except Exception as e:
                self.status_label.config(text=f"Receive error: {e}", fg="red")
                break

    
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
        