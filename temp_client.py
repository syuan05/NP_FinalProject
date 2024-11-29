import socket
import threading
import tkinter as tk
from tkinter import ttk, messagebox


class GuessNumberClient:
    def __init__(self, root):
        self.root = root
        self.root.title("1A2B 猜數字遊戲")
        self.server_ip = '127.0.0.1'
        self.port = 54321
        self.client_socket = None
        self.game_mode = None  # 儲存玩家選擇的遊戲模式
        self.is_connected = False  # 追蹤連線狀態
        self.status_label = None  # 初始化為 None，避免未定義錯誤
        self.create_mode_selection_ui()  # 創建模式選擇介面

    # 選擇遊戲模式介面
    def create_mode_selection_ui(self):
        self.mode_frame = tk.Frame(self.root)
        self.mode_frame.pack(padx=20, pady=20)

        tk.Label(self.mode_frame, text="選擇遊戲模式：", font=("Arial", 14)).pack(pady=10)

        # 單機模式按鈕
        single_button = tk.Button(self.mode_frame, text="單機模式", command=lambda: self.set_game_mode(1))
        single_button.pack(fill=tk.X, pady=5)

        # 雙人競速按鈕
        race_button = tk.Button(self.mode_frame, text="雙人競速", command=lambda: self.set_game_mode(2))
        race_button.pack(fill=tk.X, pady=5)

        # 雙人PK按鈕
        pk_button = tk.Button(self.mode_frame, text="雙人PK", command=lambda: self.set_game_mode(3))
        pk_button.pack(fill=tk.X, pady=5)

    # 設定遊戲模式並開始遊戲
    def set_game_mode(self, mode):
        self.game_mode = mode
        self.mode_frame.destroy()  # 刪除模式選擇畫面
        self.connect_server()  # 連接伺服器並初始化遊戲

    # 建立遊戲主介面
    def create_game_ui(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        # 歷史記錄顯示
        self.history = ttk.Treeview(self.frame, columns=('Guess', 'Result'), show='headings')
        self.history.heading('Guess', text='猜測數字')
        self.history.heading('Result', text='結果')
        self.history.pack(pady=5)

        # 輸入框與按鈕
        self.input_label = tk.Label(self.frame, text="輸入你的猜測：")
        self.input_label.pack()

        self.guess_entry = tk.Entry(self.frame)
        self.guess_entry.pack(pady=5)
        self.guess_entry.bind('<Return>', self.send_guess)

        self.send_button = tk.Button(self.frame, text="送出", command=self.send_guess)
        self.send_button.pack(pady=5)

        # 狀態標籤
        self.status_label = tk.Label(self.frame, text="", font=("Arial", 12))
        self.status_label.pack()

        # 離開按鈕
        self.exit_button = tk.Button(self.frame, text="離開遊戲", command=self.disconnect)
        self.exit_button.pack(pady=5)

    # 連接伺服器
    def connect_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, self.port))
            self.is_connected = True
            threading.Thread(target=self.receive_messages, daemon=True).start()

            # 傳送玩家選擇的遊戲模式到伺服器
            self.client_socket.sendall(f"MODE:{self.game_mode}".encode('utf-8'))
            self.create_game_ui()  # 建立遊戲主介面
        except Exception as e:
            messagebox.showerror("連線錯誤", f"無法連接到伺服器：{e}")
            self.root.quit()

    # 傳送猜測
    def send_guess(self, event=None):
        guess = self.guess_entry.get().strip()
        if len(guess) != 4 or not guess.isdigit() or len(set(guess)) != 4:
            messagebox.showwarning("輸入無效", "請輸入 4 位不重複的數字。")
            return
        try:
            self.client_socket.sendall(guess.encode('utf-8'))
            self.guess_entry.delete(0, tk.END)
        except Exception as e:
            if self.status_label:
                self.status_label.config(text=f"傳送錯誤：{e}", fg="red")
            self.disconnect()

    # 接收來自伺服器的訊息
    def receive_messages(self):
        while self.is_connected:
            try:
                message = self.client_socket.recv(1024).decode('utf-8')
                if "恭喜" in message or "遊戲結束" in message:
                    if self.status_label:
                        self.status_label.config(text=message, fg="green")
                    messagebox.showinfo("遊戲結束", message)
                    self.disconnect()  # 遊戲結束後自動斷線
                    break
                elif ":" in message:  # 假設收到格式為 "猜測:結果"
                    guess, result = message.split(":")
                    self.history.insert("", tk.END, values=(guess, result))
                else:
                    if self.status_label:
                        self.status_label.config(text=message)
            except Exception as e:
                if self.status_label:
                    self.status_label.config(text=f"接收錯誤：{e}", fg="red")
                break

    # 斷開連線
    def disconnect(self):
        if self.is_connected:
            self.is_connected = False
            if self.client_socket:
                try:
                    self.client_socket.close()
                except Exception as e:
                    print(f"關閉連線時發生錯誤：{e}")
        self.root.quit()


# 啟動主程式
def main():
    root = tk.Tk()
    app = GuessNumberClient(root)
    root.mainloop()


if __name__ == "__main__":
    main()
