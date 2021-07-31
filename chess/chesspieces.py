import tkinter as tk
from PIL import Image, ImageTk

#image location
sprite_folder = "chess/sprites"
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

class ChessPiece:
    def __init__(self, canvas, position, color, name):
        self.position, self.color = position, "white" if color.lower() in ["w","white"] else "black"
        self.image_path = sprite_names[color[0] + name]

        self.canvas = canvas

        self.position = position

        self.draw_image()

    def find_reals(self):
        return (
            self.position[0] * self.canvas.space_width + int((self.canvas.space_width - 64)/2),
            self.position[1] * self.canvas.space_width + int((self.canvas.space_width - 64)/2),
        )
    
    def draw_image(self):
        image = ImageTk.PhotoImage(image = Image.open(self.image_path))
        
        real_position = self.find_reals()

        if not hasattr(self.canvas._root(), "chess_piece_images"):
            self.canvas._root().chess_piece_images = [image]
        elif not isinstance(self.canvas._root().chess_piece_images, list):
            self.canvas._root().chess_piece_images = [image]
        else: self.canvas._root().chess_piece_images.append(image)

        self.image = self.canvas.create_image(real_position[0], real_position[1], anchor = tk.NW, 
          image = image, tags = "pieces")

    def find_moves(self):
        return []

    def delete(self):
        self.canvas.delete(self.image)

    def move(self, new_position):
        self.canvas.delete(self.image)

        self.position = new_position

        self.draw_image()
    
    def manage_check(self, move):
        tmp_board = [*self.canvas.board]
        if self.canvas.check_for_check(tmp_board, self.color):
            return True
        return False

class Pawn(ChessPiece):
    def __init__(self, canvas, position, color):
        ChessPiece.__init__(self, canvas, position, color, "Pawn")

        self.direction = 1 if color.lower() in ["black", "b"] else -1
        self.moved = 0

    def find_moves(self, checking = True):
        moves = []
        if 0 <= self.position[1] + self.direction < 8:
            if not(self.canvas.is_occupied(self.position[0], self.position[1] + self.direction)): 
                moves.append([self.position[0], self.position[1] + self.direction])
                if (0 <= self.position[1] + (2 * self.direction) < 8 and not
                  self.canvas.is_occupied(self.position[0], self.position[1] + (2 * self.direction))
                  and not self.moved): 
                    moves.append([self.position[0], self.position[1] + (2 * self.direction)])
        
        for i in [-1, 1]:
            if 0 <= self.position[0] + i < 8 and 0 <= self.position[1] + self.direction < 8:
                space = self.canvas.is_occupied(self.position[0] + i, self.position[1] + self.direction)
                if space:
                    if space.color != self.color:
                        moves.append([self.position[0] + i, self.position[1] + self.direction])
                space_2 = self.canvas.is_occupied(self.position[0] + i, self.position[1])
                if space_2:
                    if isinstance(space_2, Pawn) and space_2.color != self.color:
                        if space_2.moved == 1: moves.append([self.position[0] + i, self.position[1] + self.direction])

        if checking:
            for i in range(len(moves)):
                if self.manage_check(moves[i]): moves.pop()

        return moves

class Rook(ChessPiece):
    def __init__(self, canvas, position, color):
        ChessPiece.__init__(self, canvas, position, color, "Rook")

    def find_moves(self, checking = True):
        moves = []
        for i in range(self.position[1] - 1, -1, -1):
            color = self.canvas.is_occupied(self.position[0], i)
            if color: 
                if color.color != self.color: moves.append([self.position[0], i])
                break
            moves.append([self.position[0], i])
        for i in range(self.position[1] + 1, 8):
            color = self.canvas.is_occupied(self.position[0], i)
            if color: 
                if color.color != self.color: moves.append([self.position[0], i])
                break
            moves.append([self.position[0], i])
        for i in range(self.position[0] - 1, -1, -1):
            color = self.canvas.is_occupied(i, self.position[1])
            if color: 
                if color.color != self.color: moves.append([i, self.position[1]])
                break
            moves.append([i, self.position[1]])
        for i in range(self.position[0] + 1, 8):
            color = self.canvas.is_occupied(i, self.position[1])
            if color: 
                if color.color != self.color: moves.append([i, self.position[1]])
                break
            moves.append([i, self.position[1]])

        if checking:
            for i in range(len(moves)):
                if self.manage_check(moves[i]): moves.pop()

        return moves

class Bishop(ChessPiece):
    def __init__(self, canvas, position, color):
        ChessPiece.__init__(self, canvas, position, color, "Bishop")

    def find_moves(self, checking = True):
        moves = []
        for mod in range(1, min(self.position[0] + 1, self.position[1] + 1)):
            new_space = [self.position[0] - mod, self.position[1] - mod]
            space = self.canvas.is_occupied(new_space)
            if space: 
                if space.color != self.color: moves.append([self.position[0] - mod, self.position[1] - mod])
                break
            moves.append(new_space)
        for mod in range(1, min(8 - self.position[0], self.position[1] + 1)):
            new_space = [self.position[0] + mod, self.position[1] - mod]
            space = self.canvas.is_occupied(new_space)
            if space: 
                if space.color != self.color: moves.append([self.position[0] - mod, self.position[1] - mod])
                break
            moves.append(new_space)
        for mod in range(1, min(8 - self.position[0], 8 - self.position[1])):
            new_space = [self.position[0] + mod, self.position[1] + mod]
            space = self.canvas.is_occupied(new_space)
            if space: 
                if space.color != self.color: moves.append([self.position[0] - mod, self.position[1] - mod])
                break
            moves.append(new_space)
        for mod in range(1, min(self.position[0] + 1, 8 - self.position[1])):
            new_space = [self.position[0] - mod, self.position[1] + mod]
            space = self.canvas.is_occupied(new_space)
            if space: 
                if space.color != self.color: moves.append([self.position[0] - mod, self.position[1] - mod])
                break
            moves.append(new_space)
        
        if checking:
            for i in range(len(moves)):
                if self.manage_check(moves[i]): moves.pop()

        return moves

class Knight(ChessPiece):
    def __init__(self, canvas, position, color):
        ChessPiece.__init__(self, canvas, position, color, "Knight")

    def find_moves(self, checking = True):
        moves = []
        for x in [-2, 2]:
            for i in [-1, 1]:
                pos_move = [self.position[0] + i, self.position[1] + x]
                if 0 <= pos_move[0] < 8 and 0 <= pos_move[1] < 8:
                    space = self.canvas.is_occupied(pos_move)
                    if space:
                        if space.color != self.color: moves.append(pos_move)
                        continue
                    moves.append(pos_move)
        for y in [-2, 2]:
            for i in [-1, 1]:
                pos_move = [self.position[0] + y, self.position[1] + i]
                if 0 <= pos_move[0] < 8 and 0 <= pos_move[1] < 8:
                    space = self.canvas.is_occupied(pos_move)
                    if space:
                        if space.color != self.color: moves.append(pos_move)
                        continue
                    moves.append(pos_move)
        
        if checking:
            for i in range(len(moves)):
                if self.manage_check(moves[i]): moves.pop()

        return moves

class King(ChessPiece):
    def __init__(self, canvas, position, color):
        ChessPiece.__init__(self, canvas, position, color, "King")

    def find_moves(self, checking = True):
        moves = []
        for x in [-1, 0 , 1]:
            for y in [-1, 0, 1]:
                if [x, y] == [0, 0]: continue
                pos_move = [self.position[0] + x, self.position[1] + y]
                if 0 <= pos_move[0] < 8 and 0 <= pos_move[1] < 8:
                    space = self.canvas.is_occupied(pos_move)
                    if space:
                        if space.color != self.color: moves.append(pos_move)
                        continue
                    moves.append(pos_move)
        if checking:
            for i in range(len(moves)):
                if self.manage_check(moves[i]): moves.pop()

        return moves

class Queen(Rook, Bishop):
    def __init__(self, canvas, position, color):
        ChessPiece.__init__(self, canvas, position, color, "Queen")

    def find_moves(self, checking = True):
        moves = (
            *Rook.find_moves(self, checking),
            *Bishop.find_moves(self, checking),
        )

        return moves