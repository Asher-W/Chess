import numpy as np
import chess

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

class Network:
    outputs = None

    def __init__(self, shape=(), weights=[], biases=[]):
        self.shape = shape
        self.weights = weights
        self.biases = biases

    def new(self):
        for index, rows in enumerate(self.shape[1::]):
            self.weights.append(2 * np.random.rand(rows, self.shape[index]) - 1)
            self.biases.append(2 * np.random.rand(rows) - 1)
    
    def mutate(self, change_limit):
        for index, connection in enumerate(self.weights):
            weight_mutation = (2 * np.random.rand(*connection.shape) - 1) * change_limit
            self.weights[index] = connection * weight_mutation
        
        for index, layer in enumerate(self.biases):
            bias_mutation = (2 * np.random.rand(*layer.shape) - 1) * change_limit
            self.biases[index] = layer * bias_mutation

    def calculate(self, inputs):
        
        # Make nodes
        nodes = []
        for i in self.shape:
            nodes.append(np.zeros(i))

        nodes[0] = inputs

        # Calculate
        for i, layer in enumerate(nodes[1::]):
            for j in range(len(layer)):
                nodes[i + 1][j] = sigmoid(np.dot(nodes[i], self.weights[i][j]) + self.biases[i][j])
        
        return nodes[-1]

def format_board_input(board):

    # Convert board FEN to list
    fen = board.board_fen()
    board_list = []
    for i in list(fen):
        if i != '/':
            if i.isdigit() == True:
                board_list += ['0' for j in range(int(i))]
            else:
                board_list.append(i)
    
    # Convert board list to layered input board
    formatted_board = []
    pieces = ['p', 'n', 'b', 'r', 'q', 'k']
    for piece in pieces + list(''.join(pieces).upper()):
        for i in board_list:
            if i == piece:
                formatted_board.append(1)
            else:
                formatted_board.append(0)
    
    return(np.array(formatted_board))

def get_board_move(board, net_out):

    # The output layer net_out has 4160 nodes
    # The first 64 nodes encode the possible promotions in UCI format
    # The rest encode regular moves in UCI

    # 2 represents the side the pawn is on, 8 represents the file, 4 represents the piece the pawn is promoted to
    special_moves = net_out[:64]
    special_moves = special_moves.reshape((2, 8, 4)) 

    # 8 for the starting piece file, 8 for the starting piece rank, 8 for the file the piece is moved to, 8 for the rank the piece is moved to
    normal_moves = net_out[64:]
    normal_moves = normal_moves.reshape((8, 8, 8, 8)) 

    files = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
    pieces = ('n', 'b', 'r', 'q')
    move_confidence = {}

    # Create a more workable list of moves in UCI
    possible_moves = [i.uci() for i in list(board.legal_moves)]
    for move in possible_moves:
        int_move = []

        # If promotion
        if len(move) == 5:

            int_move.append(files.index(move[2]))

            # Determine if on black or white side
            if int(move[3]) == 1:
                int_move.append(0)
            else:
                int_move.append(1)
            

            int_move.append(pieces.index(move[4]))

            move_confidence[move] = special_moves[int_move[0]][int_move[1]][int_move[2]]

        # If normal
        else:

            # Convert everything to an int
            for i in list(move):
                if i.isdigit():
                    int_move.append(int(i) - 1)
                else:
                    int_move.append(files.index(i))

            move_confidence[move] = normal_moves[int_move[0]][int_move[1]][int_move[2]][int_move[3]]
    
    return max(move_confidence, key=move_confidence.get)

# net1 = Network(shape=(769, 1000, 1000, 1000, 1000, 1000, 4160))
# net1.new()
# 
# board = chess.Board()
# print(board)
# net_eval = net1.calculate(np.append(format_board_input(board), 0))
# move = get_board_move(board, net_eval)
# board.push(chess.Move.from_uci(move))
# print(board)
# net_eval = net1.calculate(np.append(format_board_input(board), 1))
# move = get_board_move(board, net_eval)
# board.push(chess.Move.from_uci(move))
# print(board)
# net_eval = net1.calculate(np.append(format_board_input(board), 0))
# move = get_board_move(board, net_eval)
# board.push(chess.Move.from_uci(move))
# print(board)
# net_eval = net1.calculate(np.append(format_board_input(board), 1))
# move = get_board_move(board, net_eval)
# board.push(chess.Move.from_uci(move))
# print(board)