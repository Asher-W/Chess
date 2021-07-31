import tkinter as tk
from PIL import Image, ImageTk
import chesspieces as cp

#font details
font, text_margin = ("Veranda", 20), 5

class ChessBoard(tk.Canvas):
    def __init__(self, root, pattern = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"):
        self.size = min(max(min(int(root.winfo_width()/8), int(root.winfo_height()/8)) * 8, 640), 1280)
        self.space_width = self.size / 8
        self.root = root
        
        tk.Canvas.__init__(self, root, width = self.size, height = self.size)
        self.pack()

        self.kings = {
          "w" : [],
          "b" : [] 
        }

        self.draw()
        self.start(pattern)

        root.bind("<Motion>", self.hover)
        self.selected = None
        root.bind("<Button-1>", self.move)

    def draw(self):
        for x in range(8):
            for y in range(8): 
                self.create_rectangle(x*self.space_width, y*self.space_width, (x+1)*self.space_width, (y+1)*self.space_width,
                  fill = "black" if (x % 2) - (y % 2) else "white")
                if not x:
                    self.create_text(text_margin, (y*self.space_width) + text_margin, anchor = tk.NW,
                      fill = "white" if y % 2 else "black", font = font, text = y + 1, tags = "labels")
            self.create_text((x + 1)*self.space_width - text_margin, 8*self.space_width - text_margin, anchor = tk.SE,
              fill = "black" if x % 2 else "white", font = font, text = chr(x + 97), tags ="labels")
            
    def start(self, pattern):
        x,y = 0,0
        self.board = [[] for i in range(8)]
        for i in pattern:
            if i == "/":
                x = 0
                y += 1
                continue
            if i.isnumeric():
                for i in range(int(i)):
                    self.board[y].append("")
                x += int(i) + 1
                continue
            i_val = ord(i)
            color = "black" if i_val > 97 else "white"
            
            i = i.lower()
            if i == "p": self.board[y].append(cp.Pawn(self, (x,y), color))
            if i == "r": self.board[y].append(cp.Rook(self, (x,y), color))
            if i == "n": self.board[y].append(cp.Knight(self, (x,y), color))
            if i == "b": self.board[y].append(cp.Bishop(self, (x,y), color))
            if i == "q": self.board[y].append(cp.Queen(self, (x,y), color))
            if i == "k": 
                self.board[y].append(cp.King(self, (x,y), color))
                self.kings[color[0]].append(self.board[y][-1])
            
            x += 1
    def get_board(self):
        board = ""
        for y in range(8):
            count = 0
            for x in range(8):
                if not self.board[y][x]:
                    count += 1
                    continue
                else:
                    space = self.board[y][x]

                    if isinstance(space, cp.Pawn):
                        new_letter = "p"
                    if isinstance(space, cp.Rook):
                        new_letter = "r"
                    if isinstance(space, cp.Knight):
                        new_letter = "n"
                    if isinstance(space, cp.Bishop):
                        new_letter = "b"
                    if isinstance(space, cp.Queen):
                        new_letter = "q"
                    if isinstance(space, cp.King):
                        new_letter = "k"
                    
                    if space.color == "white":
                        new_letter = new_letter.upper()

                    board = board + new_letter
            if count != 0: board = board + str(count)
            board = board + "/"
        
        return board
    
    def hover(self, e):
        self.root.update()
        px = self.root.winfo_pointerx() - self.winfo_rootx()
        py = self.root.winfo_pointery() - self.winfo_rooty()

        x, y = int(px / self.space_width), int(py / self.space_width)
        
        self.delete("moves")
        self.moves = []

        if not 0 <= x <= 7 or not 0 <= y <= 7: return
        
        margin = 10
        if self.board[y][x]:
            self.create_rectangle(x*self.space_width + margin, y*self.space_width + margin, 
              (x+1)*self.space_width - margin, (y+1)*self.space_width - margin, 
              tags = "moves", fill = "red")

            self.moves = self.board[y][x].find_moves()
            print(self.moves, self.kings["b"][0].position)
            for i in self.moves:
                self.create_rectangle(i[0]*self.space_width + margin, i[1]*self.space_width + margin, 
                  (i[0]+1)*self.space_width - margin, (i[1]+1)*self.space_width - margin, 
                  tags = "moves", fill = "green")

            self.tag_raise("labels")
            self.tag_raise("pieces")
    
    def move(self, e):
        self.root.update()
        px = self.root.winfo_pointerx() - self.winfo_rootx()
        py = self.root.winfo_pointery() - self.winfo_rooty()

        x, y = int(px / self.space_width), int(py / self.space_width)

        self.delete("select")
        if not 0 <= x <= 7 or not 0 <= y <= 7: return

        margin = 10
        if self.board[y][x]:
            self.create_rectangle(x*self.space_width + margin, y*self.space_width + margin, 
              (x+1)*self.space_width - margin, (y+1)*self.space_width - margin, 
              tags = "select", fill = "blue")
            
            self.root.unbind("<Motion>")
            self.root.unbind("<Button-1>")

            self.root.bind("<Button-1>", self.place_piece)
            self.root.bind("<Escape>", self.reset_click)
            self.selected = [x, y]

            self.tag_raise("labels")
            self.tag_raise("pieces")
    
    def place_piece(self, e):
        self.root.update()
        px = self.root.winfo_pointerx() - self.winfo_rootx()
        py = self.root.winfo_pointery() - self.winfo_rooty()

        x, y = int(px / self.space_width), int(py / self.space_width)

        if isinstance(self.selected, list) and  0 <= x <= 7 and 0 <= y <= 7:
            if [x, y] in self.moves:
                if isinstance(self.board[self.selected[1]][self.selected[0]], cp.Pawn):
                    if 0<=y + self.board[self.selected[1]][self.selected[0]].direction<=7 and x != self.selected[0]:
                        if (not self.board[y][x] and isinstance(self.board[y + (self.board[self.selected[1]][self.selected[0]].direction * -1)][x], cp.Pawn)
                          and self.board[y][x].color != self.board[y + (self.board[self.selected[1]][self.selected[0]].direction * -1)][x].color):
                            self.board[y + (self.board[self.selected[1]][self.selected[0]].direction * -1)][x].delete()
                            self.board[y + (self.board[self.selected[1]][self.selected[0]].direction * -1)][x] = ""
                    self.board[self.selected[1]][self.selected[0]].moved += 1
                if self.board[y][x]:self.board[y][x].delete()
                self.board[y][x] = self.board[self.selected[1]][self.selected[0]]
                self.board[y][x].move((x,y))
                self.board[self.selected[1]][self.selected[0]] = ""
        self.reset_click(e)
        self.delete("moves")
        self.delete("selected")

        print(self.board)

    def reset_click(self, e):
        self.delete("select")
        self.selected = None
        self.root.bind("<Motion>", self.hover)
        self.root.bind("<Button-1>", self.move)

    def is_occupied(self, *args):
        if isinstance(args[0], list) or isinstance(args[0], set) or isinstance(args[0], tuple):
            return self.board[args[0][1]][args[0][0]]
        if len(args) == 1 and isinstance(args[0], int):
            return self.board[int(args[0] / 8)][args[0] % 8]
        elif len(args) >= 2:
            if isinstance(args[0], int) and isinstance(args[1], int):
                return self.board[args[1]][args[0]]
        return False
    
    def check_for_check(self, board, color):
        moves = self.get_legals(board, "black" if color == "white" else "white")
        for i in self.kings[color[0]]:
            if i in moves: return True

    def get_legals(self, board, color):
        moves = []
        for y in board:
            for x in y:
                if x:
                    if x.color[0] == color[0]:
                        for i in x.find_moves(False):
                            moves.append(i)
        return moves

class QuickBoard(tk.Canvas):
    def __init__(self, root, pattern = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"):
        self.size = min(max(min(int(root.winfo_width()/8), int(root.winfo_height()/8)) * 8, 640), 1280)
        self.space_width = self.size / 8
        self.root = root

        tk.Canvas.__init__(self, root, height = self.size, width = self.size)
        self.pack()

        for x in range(8):
            for y in range(8):
                self.create_rectangle(x*self.space_width, y*self.space_width, (x+1)*self.space_width, (y+1)*self.space_width,
                  fill = "black" if (x % 2) - (y % 2) else "white")
                if not x:
                    self.create_text(text_margin, (y*self.space_width) + text_margin, anchor = tk.NW,
                      fill = "white" if y % 2 else "black", font = font, text = y + 1, tags = "labels")
            self.create_text((x + 1)*self.space_width - text_margin, 8*self.space_width - text_margin, anchor = tk.SE,
              fill = "black" if x % 2 else "white", font = font, text = chr(x + 97), tags ="labels")
    
        if pattern:
            self.draw_pieces(pattern)

    def draw_pieces(self, pattern):

        if not hasattr(self.root, "chess_piece_images"):
            self.root.chess_piece_images = []
        elif not isinstance(self.root.chess_piece_images, list):
            self.root.chess_piece_images = []

        self.delete("pieces")

        x, y = 0, 0
        self.board = [[] for i in range(8)]
        for i in pattern:
            if i == "/":
                x= 0
                y += 1
                continue
            if i.isnumeric():
                for i in range(int(i)):
                    self.board[y].append("")
                x += int(i)
                continue
            i_val = ord(i)
            color = "b" if i_val > 97 else "w"
            
            i = i.lower()
            
            if i == "p": sprite = color + "Pawn"
            if i == "r": sprite = color + "Rook"
            if i == "n": sprite = color + "Knight"
            if i == "b": sprite = color + "Bishop"
            if i == "q": sprite = color + "Queen"
            if i == "k": sprite = color + "King"

            image = ImageTk.PhotoImage(image = Image.open(cp.sprite_names[sprite]))
            self.root.chess_piece_images.append(image)
            self.create_image(x * self.space_width + int((self.space_width - 64)/2),
              y * self.space_width + int((self.space_width - 64)/2), anchor = tk.NW, 
              image = image, tags = "pieces")
            
            x += 1  

    def get_board(self):
        board = ""
        for y in range(8):
            count = 0
            for x in range(8):
                if not self.board[y][x]:
                    count += 1
                    continue
                else:
                    if self.board[y][x][1:] == "Knight":
                        new_letter = "n"
                    else:
                        new_letter = self.board[y][x][1].lower()
                    
                    if self.board[y][x][0] == "w":
                        new_letter = new_letter.upper()
                    
                    board = board + new_letter
            if count != 0: board = board + str(count)
            board = board + "/"
        
        return board