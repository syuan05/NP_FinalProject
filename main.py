import tkinter as tk
from tkinter import messagebox


class GoGame:
    def __init__(self, board_size=19):
        self.board_size = board_size
        self.current_play = 'A'
        self.board = [['.' for _ in range(board_size)] for _ in range(board_size)]
        self.history = []

        self.window = tk.Tk()
        self.window.title("GoGame")

        self.canvas_size = 608
        self.cell_size = self.canvas_size // board_size  # 棋格大小
        self.canvas = tk.Canvas(self.window, width=self.canvas_size, height=self.canvas_size, background='#DEB887')
        self.canvas.pack()

        self.canvas.bind("<Button-1>", self.onclick)

        self.draw_board()

    def draw_board(self):
        for i in range(self.board_size):
            self.canvas.create_line(self.cell_size * i, 0, self.cell_size * i, self.canvas_size)
            self.canvas.create_line(0, self.cell_size * i, self.canvas_size, self.cell_size * i)

    def onclick(self, event):
        x = round(event.x / self.cell_size)
        y = round(event.y / self.cell_size)
        print(f'x = {x}, y = {y}')  # 記得改成正確的 x 和 y 值
        if self.can_move(y, x):
            self.place_stone(y, x)  # 落子
            self.draw_stone(y, x)   # 畫棋子
            self.switch_player()    # 切換玩家

    def can_move(self, y, x):
        if x < 0 or x >= self.board_size or y < 0 or y >= self.board_size:
            messagebox.showwarning("Invalid Move", "The move is out of bounds.")
            return False
        if self.board[y][x] != '.':
            messagebox.showwarning("Invalid Move", "The spot is already taken!")
            return False
        return True

    def place_stone(self, y, x):
        self.history.append((y, x, self.current_play))
        self.board[y][x] = self.current_play

    def draw_stone(self, y, x):
        x1 = x * self.cell_size - self.cell_size // 4
        x2 = x * self.cell_size + self.cell_size // 4
        y1 = y * self.cell_size - self.cell_size // 4
        y2 = y * self.cell_size + self.cell_size // 4
        if self.current_play == 'A':  # 黑棋
            self.canvas.create_oval(x1, y1, x2, y2, fill='black')
        else:  # 白棋
            self.canvas.create_oval(x1, y1, x2, y2, fill='white')


    # def check(self, y, x):
        
    def switch_player(self):
        if self.current_play == 'A':  # 如果當前玩家是A，則切換為B
            self.current_play = 'B'
        else:  # 否則切換為A
            self.current_play = 'A'
    def start(self):
        self.window.mainloop()


if __name__ == "__main__":
    game = GoGame()
    game.start()