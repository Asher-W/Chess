#image location
sprite_folder = "Sprites"
sprite_names = {
  "wPawn" : "/".join([sprite_folder + "wPawn"]),
  "bPawn" : "/".join([sprite_folder + "bPawn"]),
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
    def __init__(self, window):
        pass

    def start(self):
        pass

class ChessPiece:
    def __init__(self):
        pass

class Pawn(ChessPiece):
    def __init__(self, window, position, color):
        self.position = position

        