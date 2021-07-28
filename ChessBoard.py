#image location
sprite_folder = "Sprites"
sprite_names = {
  "wPawn" : "/".join([sprite_folder + "WhitePawn.png"]),
  "bPawn" : "/".join([sprite_folder + "BlackPawn.png"]),
  "wRook" : "/".join([sprite_folder + "WhiteRook.png"]),
  "bRook" : "/".join([sprite_folder + "BlackRook.png"]),
  "wBishop" : "/".join([sprite_folder + "WhiteBishop.png"]),
  "bBishop" : "/".join([sprite_folder + "BlackBishop.png"]),
  "wKnight" : "/".join([sprite_folder + "WhiteKnight.png"]),
  "bKnight" : "/".join([sprite_folder + "BlackKnight.png"]),
  "wKing" : "/".join([sprite_folder + "WhiteKing.png"]),
  "bKing" : "/".join([sprite_folder + "BlackKing.png"]),
  "wQueen" : "/".join([sprite_folder + "WhiteQueen.png"]),
  "bQueen" : "/".join([sprite_folder + "BlackQueen.png"])
}

'''
-Sprites
    -wPawn
    -bPawn
    -wKing 
    ...

-Sprites
    -Pawn
        -White
        -Black
    -King
        -White
        -Black
    ...
'''

class ChessBoard:
    def __init__(self, canvas):
        pass

    def start(self):
        pass

class ChessPiece:
    def __init__(self, canvas, position, color, name):
        self.position = position
        self.image_path = sprite_names["w" + name] if color.lower() in ["w","white"] else sprite_names["b" + name]
        
        self.position = position
        '''self.real_position = (
          (canvas.winfo_width / 8) * position[0],
          (canvas.winfo_height / 8) * position[1]
        )'''
        
        self.canvas = canvas

    def draw_spots(self, moves):
        pass

class Pawn(ChessPiece):
    def __init__(self, canvas, position, color):
        ChessPiece.__init__(self, canvas, position, color, "Pawn")

        self.direction = 1 if color.lower() in ["white", "w"] else -1
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
        ChessPiece.__init__(self, canvas, position, color, "Bishop")

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