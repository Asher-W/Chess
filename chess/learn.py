import numpy as np
import chess
import time # Run speed tests
import copy
from itertools import permutations
import random
import pickle

t1 = time.time()

def sigmoid(x):
    return 1 / (1 + np.exp(-x))

class Network:
    outputs = None
    move_history = []
    move_confidence = {}
    move = None
    points = 0

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
            self.weights[index] = connection + weight_mutation
        
        for index, layer in enumerate(self.biases):
            bias_mutation = (2 * np.random.rand(*layer.shape) - 1) * change_limit
            self.biases[index] = layer + bias_mutation

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

        self.move = np.random.choice(list(sorted_move_confidence.keys()), 1, p=list(sorted_move_confidence.values()))[0]
    
    def exec_move(self):
        self.get_board_input()
        self.calculate()
        self.get_move_confidence()
        self.select_move()
        self.board.push(chess.Move.from_uci(self.move))

def run_game(white_net, black_net, max_moves, cmd_print=False):
    game_board = chess.Board()
    
    white_net.board = game_board
    white_net.side = 0

    black_net.board = game_board
    black_net.side = 1

    if cmd_print:
            print(game_board, '\n')

    total_moves = 0
    while True:
        # white - 0, black - 1
        if total_moves % 2 == 0:
            white_net.exec_move()
        else:
            black_net.exec_move()
        
        if cmd_print:
            print(game_board, '\n')
        
        final_fen = game_board.board_fen()

        if game_board.is_checkmate():
            if total_moves % 2 == 0:
                white_net.points += 10
                black_net.points += 1
                del game_board
                return 'white win', final_fen
            else:
                white_net.points += 1
                black_net.points += 10
                del game_board
                return 'black win', final_fen
        elif game_board.is_stalemate():
            white_net.points += 5
            black_net.points += 5
            del game_board
            return 'stalemate', final_fen
        elif game_board.is_insufficient_material():
            del game_board
            return 'insufficient material', final_fen
        elif total_moves == max_moves:
            white_net.points -= 2
            black_net.points -= 2
            del game_board
            return 'maxed', final_fen
        
        total_moves += 1

def run_generation(parent, children_count, games_per_child, mutate_limit): # Rename parent to parent_nets if you want to test multiple parents
    if children_count % (games_per_child + 1) != 0:
        raise Exception('children_count and games_per_child restritions impossible.')
    
    # Uncomment to test multiple parents
    # if children_count % len(parent_nets) != 0:
    #     raise Exception('children_count and parent_net restritions impossible.')

    children = []
    games_child_played = []
    log_games_played = []
    
    # Comment the 3 lines below to test multiple parents
    for x in range(children_count):
        children.append(copy.deepcopy(parent))
        games_child_played.append(0)
    
    # Uncomment to test multiple parents
    # for parent in parent_nets:
    #     for x in range(int(children_count / len(parent_nets))):
    #         children.append(copy.deepcopy(parent))
    #         games_child_played.append(0)

    print('children created') # ---
    
    for child in children:
        child.mutate(mutate_limit)
    print('children mutated') # ---
    
    possible_games = list(permutations(list(range(children_count)), 2))

    while True:
        possible_game = random.choice(possible_games)
        if (not possible_game in log_games_played) and (games_child_played[possible_game[0]] < games_per_child) and (games_child_played[possible_game[1]] < games_per_child):
            net1 = children[possible_game[0]]
            net2 = children[possible_game[1]]
        
            print(run_game(net1, net2, 400, cmd_print=True))
            log_games_played.append(possible_game)
            games_child_played[possible_game[0]] += 1
            games_child_played[possible_game[1]] += 1

            if set(games_child_played) == {games_per_child}:
                break
    
    scores = []
    for child in children:
        scores.append(child.points)
    
    # Note - someone should probably make something to sort the children and scores but it keeps getting angry and I don't have the time to fix a problem I can only test every 40 minutes

    # Sure, I could change the code to have less downtime but I don't feel like doing that

    # Something to delete the unused children after this function is run should also be added

    return children, scores

def evolution(generations):
    pass

# Demonstration
def main():

    parent1 = Network(shape=(769, 1000, 1000, 1000, 1000, 1000, 4160))
    parent1.new()

    # Uncomment to test multiple parents
    # parent2 = Network(shape=(769, 1000, 1000, 1000, 1000, 1000, 4160))
    # parent2.new()

    # parent3 = Network(shape=(769, 1000, 1000, 1000, 1000, 1000, 4160))
    # parent3.new()

    # parent4 = Network(shape=(769, 1000, 1000, 1000, 1000, 1000, 4160))
    # parent4.new()

    # parent5 = Network(shape=(769, 1000, 1000, 1000, 1000, 1000, 4160))
    # parent5.new()

    print('parents created')

    # Comment to test multiple parents
    nets, points = run_generation(parent1, 50, 4, 0.3)

    # Uncomment to test multiple parents
    # nets, points = run_generation([parent1, parent2, parent3, parent4, parent5], 50, 4, 0.3)
    print(nets, points)

main()
t2 = time.time()
print(t2 - t1)

# All changes to switch to multiple parents are in the main() and run_generation() functions