import tkinter as tk
from PIL import ImageTk, Image

#font details
font, text_margin = ("Veranda", 20), 5

#image location
sprite_folder = "Sprites"
sprite_names = {
  "wPawn" : "/".join([sprite_folder, "WhitePawn.png"]),
  "bPawn" : "/".join([sprite_folder, "BlackPawn.png"]),
  "wRook" : "/".join([sprite_folder, "WhiteRook.png"]),
  "bRook" : "/".join([sprite_folder, "BlackRook.png"]),
  "wBishop" : "/".join([sprite_folder, "WhiteBishop.png"]),
  "bBishop" : "/".join([sprite_folder, "BlackBishop.png"]),
  "wKnight" : "/".join([sprite_folder, "WhiteKnight.png"]),
  "bKnight" : "/".join([sprite_folder, "BlackKnight.png"]),
  "wKing" : "/".join([sprite_folder, "WhiteKing.png"]),
  "bKing" : "/".join([sprite_folder, "BlackKing.png"]),
  "wQueen" : "/".join([sprite_folder, "WhiteQueen.png"]),
  "bQueen" : "/".join([sprite_folder, "BlackQueen.png"])
}

class ChessBoard(tk.Canvas):
    def __init__(self, root, pattern = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"):
        self.size = min(max(min(int(root.winfo_width()/8), int(root.winfo_height()/8)) * 8, 640), 1280)
        self.space_width = self.size / 8
        self.root = root
        
        tk.Canvas.__init__(self, root, width = self.size, height = self.size)
        self.pack()

        self.draw()
        self.start(pattern)

        root.bind("<Motion>", lambda e: self.hover())

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
                x += int(i)
                continue
            i_val = ord(i)
            color = "black" if i_val > 97 else "white"
            
            i = i.lower()
            if i == "p": self.board[y].append(Pawn(self, (x,y), color))
            if i == "r": self.board[y].append(Rook(self, (x,y), color))
            if i == "n": self.board[y].append(Knight(self, (x,y), color))
            if i == "b": self.board[y].append(Bishop(self, (x,y), color))
            if i == "q": self.board[y].append(Queen(self, (x,y), color))
            if i == "k": self.board[y].append(King(self, (x,y), color))
            
            x += 1
    
    def hover(self):
        self.root.update()
        px = self.root.winfo_pointerx() - self.winfo_rootx()
        py = self.root.winfo_pointery() - self.winfo_rooty()

        x, y = int(px / self.space_width), int(py / self.space_width)
        
        self.delete("moves")

        if not 0 <= x <= 7 or not 0 <= y <= 7: return
        
        margin = 10
        if self.board[y][x]:
            self.create_rectangle(x*self.space_width + margin, y*self.space_width + margin, 
              (x+1)*self.space_width - margin, (y+1)*self.space_width - margin, 
              tags = "moves", fill = "red")

            moves = self.board[y][x].find_moves()
            for i in moves:
                self.create_rectangle(i[0]*self.space_width + margin, i[1]*self.space_width + margin, 
                  (i[0]+1)*self.space_width - margin, (i[1]+1)*self.space_width - margin, 
                  tags = "moves", fill = "green")

            self.tag_raise("labels")
            self.tag_raise("pieces")

class ChessPiece:
    def __init__(self, canvas, position, color, name):
        self.position = position
        self.image_path = sprite_names["w" + name] if color.lower() in ["w","white"] else sprite_names["b" + name]
        
        self.canvas = canvas

        self.position = position
        real_position = self.find_real()
        
        chess_piece_images = ImageTk.PhotoImage(image = Image.open(self.image_path))

        if not hasattr(canvas._root(), "chess_piece_images"):
            canvas._root().chess_piece_images = [chess_piece_images]
        elif not isinstance(canvas._root().chess_piece_images, list):
            canvas._root().chess_piece_images = [chess_piece_images]
        else: canvas._root().chess_piece_images.append(chess_piece_images)

        canvas.create_image(real_position[0], real_position[1], anchor = tk.NW, 
          image = chess_piece_images, tags = "pieces")
    def find_real(self):
        return (
            self.position[0] * self.canvas.space_width + int((self.canvas.space_width - 64)/2),
            self.position[1] * self.canvas.space_width + int((self.canvas.space_width - 64)/2),
        )
    def find_moves(self):
        return []

    def draw_spots(self, moves):
        pass

class Pawn(ChessPiece):
    def __init__(self, canvas, position, color):
        ChessPiece.__init__(self, canvas, position, color, "Pawn")

        self.direction = 1 if color.lower() in ["black", "b"] else -1
        self.moved = False

    def find_moves(self):
        moves = []
        # need to check if space is filled by another piece (not yet implemented)
        if not self.moved:  
            if 0 <= self.position[1] + self.direction < 8: 
                moves.append([self.position[0], self.position[1] + self.direction])
                if 0 <= self.position[1] + (2 * self.direction) < 8: 
                    moves.append([self.position[0], self.position[1] + (2 * self.direction)])
        else:
            if 0 <= self.position[1] + self.direction < 8: 
                moves.append([self.position[0], self.position[1] + self.direction])

        return moves

class Rook(ChessPiece):
    def __init__(self, canvas, position, color):
        ChessPiece.__init__(self, canvas, position, color, "Rook")

    def find_moves(self):
        moves = []
        # need to check if space is filled by another piece (not yet implemented)
        for i in range(self.position[1] - 1, -1, -1):
            moves.append([self.position[0], i])
        for i in range(self.position[1] + 1, 8):
            moves.append([self.position[0], i])
        for i in range(self.position[0] - 1, -1, -1):
            moves.append([i, self.position[0]])
        for i in range(self.position[0] + 1, 8):
            moves.append([i, self.position[0]])
        
        return moves

class Bishop(ChessPiece):
    def __init__(self, canvas, position, color):
        ChessPiece.__init__(self, canvas, position, color, "Bishop")

    def find_moves(self):
        moves = []
        # need to check if space is filled by another piece (not yet implemented)
        for mod in range(1, min(self.position[0] + 1, self.position[1] + 1)):
            moves.append([self.position[0] - mod, self.position[1] - mod])
        for mod in range(1, min(8 - self.position[0], self.position[1] + 1)):
            moves.append([self.position[0] + mod, self.position[1] - mod])
        for mod in range(1, min(8 - self.position[0], 8 - self.position[1])):
            moves.append([self.position[0] + mod, self.position[1] + mod])
        for mod in range(1, min(self.position[0] + 1, 8 - self.position[1])):
            moves.append([self.position[0] - mod, self.position[1] + mod])
        
        return moves

class Knight(ChessPiece):
    def __init__(self, canvas, position, color):
        ChessPiece.__init__(self, canvas, position, color, "Knight")

    def find_moves(self):
        moves = []
        # need to check if space is filled by another piece (not yet implemented)
        for x in [-2, 2]:
            for i in [-1, 1]:
                pos_move = [self.position[0] + i, self.position[1] + x]
                if 0 <= pos_move[0] < 8 and 0 <= pos_move[1] < 8:
                    moves.append(pos_move)
        for y in [-2, 2]:
            for i in [-1, 1]:
                pos_move = [self.position[0] + y, self.position[1] + i]
                if 0 <= pos_move[0] < 8 and 0 <= pos_move[1] < 8:
                    moves.append(pos_move)
        
        return moves

class King(ChessPiece):
    def __init__(self, canvas, position, color):
        ChessPiece.__init__(self, canvas, position, color, "King")

    def find_moves(self):
        moves = []
        # need to check if space is filled by another piece (not yet implemented)
        for x in [-1, 0 , 1]:
            for y in [-1, 0, 1]:
                if [x, y] == [0, 0]: continue
                new_pos = [self.position[0] + x, self.position[1] + y]
                if not 0 <= new_pos[1] < 8: break
                if 0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8:
                    moves.append(new_pos)
        
        return moves

class Queen(Rook, Bishop):
    def __init__(self, canvas, position, color):
        ChessPiece.__init__(self, canvas, position, color, "Queen")

    def find_moves(self):
        moves = (
            *Rook.find_moves(self),
            *Bishop.find_moves(self),
        )

        return moves