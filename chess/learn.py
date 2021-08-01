import numpy as np
import os

from chessboard import QuickBoard
import tkinter

from numpy.random.mtrand import rand

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
            self.weights.append(2 * np.random.rand(rows, self.shape[index]).astype(np.float16) - 1)
            self.biases.append(2 * np.random.rand(rows).astype(np.float16) - 1)
    
    def mutate(self, mutation_rate):
        for index, connection in enumerate(self.weights):
            weight_mutation = (2 * np.random.rand(*connection.shape) - 1) * mutation_rate
            self.weights[index] = connection + weight_mutation
        
        for index, layer in enumerate(self.biases):
            bias_mutation = (2 * np.random.rand(*layer.shape) - 1) * mutation_rate
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
                nodes[i + 1][j] = sigmoid(np.dot(nodes[i], self.weights[i][j]) - self.biases[i][j])
        
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

def run_game(white_net, black_net, max_moves, canvas, cmd_print=False):
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
        
        canvas.draw_pieces(final_fen)
        canvas.root.update()
        

        if game_board.is_checkmate():
            if total_moves % 2 == 0:
                white_net.points += 10
                black_net.points -= 5
                del game_board
                return 'white win', final_fen
            else:
                white_net.points -= 5
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
            white_net.points -= 8
            black_net.points -= 8
            del game_board
            return 'max moves reached', final_fen
        
        total_moves += 1

def produce_children(child_count, shape, mutation_rate, parents):
    children = []
    for i in range(child_count):
        new_bias = []
        new_weights = []

        for index in range(len(shape[1::])):
            new_weights.append(random.choice(parents).weights[index])
            new_bias.append(random.choice(parents).biases[index])
        
        children.append(Network(shape = shape, weights = new_weights, biases = new_bias))

        children[-1].mutate(mutation_rate)
    
    return children

def run_generation(children_count, games_per_child, mutation_rate, parents, canvas): # Rename parent to parent_nets if you want to test multiple parents
    if children_count % (games_per_child + 1) != 0:
        raise Exception('children_count and games_per_child restritions impossible.')

    children = produce_children(children_count, parents[0].shape, mutation_rate, parents)
    games_child_played = [0 for i in children]
    log_games_played = []
    
    print('\n', 'children created') # ---
    
    possible_games = list(permutations(list(range(children_count)), 2))

    random.shuffle(possible_games)
    for possible_game in possible_games:
        if (not possible_game in log_games_played) and (games_child_played[possible_game[0]] < games_per_child) and (games_child_played[possible_game[1]] < games_per_child):
            net1 = children[possible_game[0]]
            net2 = children[possible_game[1]]
        
            print(run_game(net1, net2, 400, canvas, cmd_print=False))
            log_games_played.append(possible_game)
            games_child_played[possible_game[0]] += 1
            games_child_played[possible_game[1]] += 1

            if set(games_child_played) == {games_per_child}:
                break
    
    # Note - someone should probably make something to sort the children and scores but it keeps getting angry and I don't have the time to fix a problem I can only test every 40 minutes

    # Sure, I could change the code to have less downtime but I don't feel like doing that

    # Something to delete the unused children after this function is run should also be added
    
    children.sort(reverse=True, key = lambda c:c.points)
    return children[:len(parents)]
    
def run_evolution(shape, epochs = 5, parent_count = 5, child_count = 50, game_count = 5, mutation_rate = 0.5, mutation_reduction_rate = 9/10, save_stage = 10, parents = None):
    root = tkinter.Tk()
    canvas = QuickBoard(root)

    if not isinstance(parents, list): parents = [Network(shape = shape) for i in range(parent_count)]
    if not all(isinstance(i, Network) for i in parents): parents = [Network(shape = shape) for i in range(parent_count)]

    for i in parents: i.new()
    # uncomment for a limited run-time
    # for i in range(epochs):
    gen = 1
    while 1:
        parents = run_generation(child_count, game_count, min(mutation_rate * (mutation_reduction_rate ** gen), 1), parents, canvas)
        if gen % save_stage == 0:
            outfile = open('Outputs/networks_Gen_{0}.p'.format(gen),'wb')
            pickle.dump(parents, outfile)
            outfile.close()

            old_file = "Outputs/networks_Gen_{0}.p".format(gen - (save_stage * 3))
            if os.path.exists(old_file): os.remove(old_file)

            print("partially trained  AI version saved")
        print("generation {0} finished - top points: {1}".format(gen, parents[0].points))

        gen += 1
    
    root.mainloop()
    
    return parents[0]

def load_save(file_name):
    file = open(file_name)
    return pickle.load(file)

# Demonstration
def main():
    template = Network(shape=(769, 1000, 1000, 1000, 1000, 1000, 4160))
    template.new()

    print('parents created')

    file = "Outputs/networks_Gen_10.p"

    # Comment to test multiple parents
    final = run_evolution(shape = (769, 1000, 1000, 1000, 1000, 1000, 4160), epochs = 150, parent_count = 3, child_count = 16, game_count = 3, mutation_rate = 0.3, save_stage = 5)

    print(final)

    outfile = open('networks.p','wb')
    pickle.dump(final, outfile)
    outfile.close()

main()
t2 = time.time()
print(t2 - t1)

# All changes to switch to multiple parents are in the main() and run_generation() functions