import numpy as np
import chess
import random
#from chessboard import display

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

class Network:
    outputs = None
    move_history = []
    move_confidence = {}
    move = None

    def __init__(self, shape=(), weights=[], biases=[], inputs=np.array([]), board=None, side=None):
        self.shape = shape
        self.weights = weights
        self.biases = biases
        self.inputs = inputs
        self.board = board
        self.side = side

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

    def calculate(self):
        
        # Make nodes
        nodes = []
        for i in self.shape:
            nodes.append(np.zeros(i))

        nodes[0] = self.inputs

        # Calculate
        for i, layer in enumerate(nodes[1::]):
            for j in range(len(layer)):
                nodes[i + 1][j] = sigmoid(np.dot(nodes[i], self.weights[i][j]) + self.biases[i][j])
        
        self.outputs = nodes[-1]
    
    # ---
    # Chess specific methods
    # ---

    def get_board_input(self):

        # Convert board FEN to list
        fen = self.board.board_fen()
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
        
        formatted_board.append(self.side)
        self.inputs = np.array(formatted_board)

    def get_move_confidence(self):

        # The output layer net_out has 4160 nodes
        # The first 64 nodes encode the possible promotions in UCI format
        # The rest encode regular moves in UCI

        # 2 represents the side the pawn is on, 8 represents the file, 4 represents the piece the pawn is promoted to
        special_moves = self.outputs[:64]
        special_moves = special_moves.reshape((2, 8, 4)) 

        # 8 for the starting piece file, 8 for the starting piece rank, 8 for the file the piece is moved to, 8 for the rank the piece is moved to
        normal_moves = self.outputs[64:]
        normal_moves = normal_moves.reshape((8, 8, 8, 8)) 

        files = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
        pieces = ('n', 'b', 'r', 'q')
        possible_move_confidence = {}

        # Create a more workable list of moves in UCI
        possible_moves = [i.uci() for i in list(self.board.legal_moves)]
        for move in possible_moves:
            int_move = []

            # If promotion
            if len(move) == 5:

                # Determine if on black or white side
                if int(move[3]) == 1:
                    int_move.append(0)
                else:
                    int_move.append(1)
            
                int_move.append(files.index(move[2]))
                int_move.append(pieces.index(move[4]))

                possible_move_confidence[move] = special_moves[int_move[0]][int_move[1]][int_move[2]]

            # If normal
            else:

                # Convert everything to an int
                for i in list(move):
                    if i.isdigit():
                        int_move.append(int(i) - 1)
                    else:
                        int_move.append(files.index(i))

                possible_move_confidence[move] = normal_moves[int_move[0]][int_move[1]][int_move[2]][int_move[3]]

        #max(possible_move_confidence, key=possible_move_confidence.get)
        self.move_confidence = possible_move_confidence
    
    def select_move(self):
        list_move_confidence = sorted(self.move_confidence.items(), key=lambda x:x[1])
        sorted_move_confidence = dict(list_move_confidence)

        # Temperature
        confidence_weight_sum = 0
        for move in sorted_move_confidence:
            confidence_weight_sum += sorted_move_confidence[move]

        for weight in sorted_move_confidence:
            sorted_move_confidence[weight] = sorted_move_confidence[weight] / confidence_weight_sum

        moves_bag = []
        self.move = np.random.choice(list(sorted_move_confidence.keys()), 1, p=list(sorted_move_confidence.values()))[0]
    
    def exec_move(self):
        self.get_board_input()
        self.calculate()
        self.get_move_confidence()
        self.select_move()
        self.board.push(chess.Move.from_uci(self.move))

# white - 0, black - 1

# Demonstration
def main():
    board = chess.Board()
    print(board, '\n')

    net1 = Network(shape=(769, 1000, 1000, 1000, 1000, 1000, 4160), board=board, side=0)
    net1.new()

    net2 = Network(shape=(769, 1000, 1000, 1000, 1000, 1000, 4160), board=board, side=1)
    net2.new()

    total_moves = 0
    while True:
        if total_moves % 2 == 0:
            net1.exec_move()
        else:
            net2.exec_move()

        print(board, '\n')

        if board.is_checkmate():
            print('Win')
            break
        elif board.is_stalemate():
            print('Stalemate')
            break
        elif total_moves == 400:
            print('Too many moves')
            break
        
        total_moves += 1

main()