import socket
import threading
import random

server_ip = '127.0.0.1'
server_port = 54321

clients = []
client_lock = threading.Lock()

# 驗證猜測是否合法 (4 位不重複數字)
def is_valid_guess(guess):
    return len(guess) == 4 and guess.isdigit() and len(set(guess)) == 4

# 計算 1A2B 結果
def calculate_result(guess, answer):
    A_count = sum(1 for i in range(4) if guess[i] == answer[i])  # 完全正確的位置與數字
    B_count = sum(1 for i in range(4) for j in range(4) if guess[i] == answer[j] and i != j)  # 數字正確但位置錯誤
    return A_count, B_count

# 單機模式邏輯
def handle_single_mode(client_socket, address):
    answer = ''.join(random.sample('0123456789', 4))  # 隨機生成 4 位數字
    client_socket.sendall("單機模式開始！試著猜出 4 位數字，格式如：1234\n".encode('utf-8'))

    while True:
        guess = client_socket.recv(1024).decode('utf-8').strip()
        if not is_valid_guess(guess):
            client_socket.sendall("無效輸入！請輸入 4 位不重複的數字。\n".encode('utf-8'))
            continue
        
        A, B = calculate_result(guess, answer)
        if A == 4:
            client_socket.sendall(f"恭喜！你猜對了！答案是 {answer}。\n".encode('utf-8'))
            break
        else:
            client_socket.sendall(f"{A}A{B}B，繼續猜！\n".encode('utf-8'))

    client_socket.close()

# 雙人競速模式邏輯
def handle_dual_race_mode(player1, player2):
    answer = ''.join(random.sample('0123456789', 4))  # 隨機生成 4 位數字
    player1.sendall("雙人競速模式開始！等待對手的回合...\n".encode('utf-8'))
    player2.sendall("雙人競速模式開始！等待對手的回合...\n".encode('utf-8'))

    turn = 0  # 0 表示玩家1回合，1 表示玩家2回合
    while True:
        current_player = player1 if turn == 0 else player2
        current_player.sendall("你的回合！請輸入 4 位數字：\n".encode('utf-8'))

        guess = current_player.recv(1024).decode('utf-8').strip()
        if not is_valid_guess(guess):
            current_player.sendall("無效輸入！請輸入 4 位不重複的數字。\n".encode('utf-8'))
            continue
        
        A, B = calculate_result(guess, answer)
        if A == 4:
            current_player.sendall(f"恭喜！你猜對了！答案是 {answer}。\n".encode('utf-8'))
            other_player = player2 if turn == 0 else player1
            other_player.sendall(f"對手已經猜出答案！答案是 {answer}。遊戲結束！\n".encode('utf-8'))
            break
        else:
            current_player.sendall(f"{A}A{B}B，等待對手的回合...\n".encode('utf-8'))

        turn = 1 - turn  # 切換回合

    player1.close()
    player2.close()

# 雙人PK模式邏輯
def handle_dual_pk_mode(player1, player2):
    # 讓玩家分別輸入自己的題目
    player1.sendall("請輸入你的題目 (4 位不重複數字)：\n".encode('utf-8'))
    player2.sendall("請輸入你的題目 (4 位不重複數字)：\n".encode('utf-8'))

    answer1 = player1.recv(1024).decode('utf-8').strip()
    answer2 = player2.recv(1024).decode('utf-8').strip()

    if not is_valid_guess(answer1) or not is_valid_guess(answer2):
        player1.sendall("題目無效，遊戲結束！\n".encode('utf-8'))
        player2.sendall("題目無效，遊戲結束！\n".encode('utf-8'))
        player1.close()
        player2.close()
        return

    player1.sendall("你的題目已設定。等待對手猜測...\n".encode('utf-8'))
    player2.sendall("你的題目已設定。等待對手猜測...\n".encode('utf-8'))

    turn = 0  # 0 表示玩家1猜測，1 表示玩家2猜測
    while True:
        current_player = player1 if turn == 0 else player2
        opponent_answer = answer2 if turn == 0 else answer1

        current_player.sendall("你的回合！請輸入 4 位數字：\n".encode('utf-8'))
        guess = current_player.recv(1024).decode('utf-8').strip()

        if not is_valid_guess(guess):
            current_player.sendall("無效輸入！請輸入 4 位不重複的數字。\n".encode('utf-8'))
            continue
        
        A, B = calculate_result(guess, opponent_answer)
        if A == 4:
            current_player.sendall(f"恭喜！你猜對了！對方的答案是 {opponent_answer}。\n".encode('utf-8'))
            other_player = player2 if turn == 0 else player1
            other_player.sendall(f"對手已經猜出你的答案！答案是 {opponent_answer}。遊戲結束！\n".encode('utf-8'))
            break
        else:
            current_player.sendall(f"{A}A{B}B，等待對手的回合...\n".encode('utf-8'))

        turn = 1 - turn  # 切換回合

    player1.close()
    player2.close()

# 處理客戶端連線
def handle_client(client_socket, address):
    client_socket.sendall("歡迎來到 1A2B 猜數字遊戲！\n請選擇模式：\n1. 單機模式\n2. 雙人競速\n3. 雙人PK\n".encode('utf-8'))
    mode = client_socket.recv(1024).decode('utf-8').strip()

    if mode == "1":
        handle_single_mode(client_socket, address)
    elif mode == "2":
        with client_lock:
            clients.append(client_socket)
            if len(clients) >= 2:
                player1 = clients.pop(0)
                player2 = clients.pop(0)
                threading.Thread(target=handle_dual_race_mode, args=(player1, player2)).start()
    elif mode == "3":
        with client_lock:
            clients.append(client_socket)
            if len(clients) >= 2:
                player1 = clients.pop(0)
                player2 = clients.pop(0)
                threading.Thread(target=handle_dual_pk_mode, args=(player1, player2)).start()
    else:
        client_socket.sendall("無效的模式選擇，請重新連線。\n".encode('utf-8'))
        client_socket.close()

# 主伺服器程式
def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((server_ip, server_port))
    server_socket.listen(5)
    print(f"伺服器已啟動，等待連線... (IP: {server_ip}, Port: {server_port})")

    while True:
        client_socket, address = server_socket.accept()
        print(f"新的連線：{address}")
        threading.Thread(target=handle_client, args=(client_socket, address)).start()


if __name__ == "__main__":
    main()
