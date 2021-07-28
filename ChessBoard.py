from tkinter import Canvas, BOTH

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
color_1 = "#000"
color_2 = "#fff"
label_size = 16

class ChessBoard(Canvas):
    def __init__(self, root):
        root.update()
        space_width = int(min(root.winfo_width(), root.winfo_height()) / 8)
        width =  space_width * 8
        Canvas.__init__(self, root, width = width, height = width)

        letter_spacing = int(label_size / 10) + 3
        for x in range(8):
            for y in range(8):
                if y % 2: 
                    box_color = color_1 if x % 2 else color_2
                    text_color = color_1 if not x % 2 else color_2
                else: 
                    box_color = color_1 if not x % 2 else color_2
                    text_color = color_1 if x % 2 else color_2
                self.create_rectangle(x * space_width, y * space_width, ((x + 1) * space_width) - 1, ((y + 1) * space_width) - 1, fill = box_color)
                
                if not x:
                    self.create_text(x * space_width + int(label_size / 2) + letter_spacing, 
                      y * space_width + int(label_size / 2) + letter_spacing, text = y, 
                      fill = text_color, font = ("Veranda", label_size))
                if y == 7:
                    self.create_text((x + 1) * space_width - int(label_size / 2) - letter_spacing, 
                      (y + 1) * space_width - int(label_size / 2) - letter_spacing, text = chr(x + 97), 
                      fill = text_color, font = ("Veranda", label_size))

        self.pack()

    def start(self):
        pass

class ChessPiece:
    def __init__(self, canvas, position, color, name):
        self.position = position
        self.image_path = sprite_names["w" + name] if color.lower() in ["w","white"] else sprite_names["b" + name]

        image = ImageTk.PhotoImage(Image.open)
        canvas.create_image
        
        self.position = position
        '''self.real_position = (
          (canvas.winfo_width() / 8) * position[0],
          (canvas.winfo_height() / 8) * position[1]
        )'''
        
        self.canvas = canvas

        canvas.create_image()

    def find_moves(self):
        return []

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