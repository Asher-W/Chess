from learn import *
import chessboard as cb

import pickle as p
import tkinter as tk

def compare(input_file, games = 50):
    test_object = Network(shape = (769, 1000, 1000, 1000, 1000, 4160))
    test_object.new()

    with open(input_file, "rb") as file:
        model = p.load(file)[0]
    
    root = tk.Tk()
    canvas = QuickBoard(root)
    outcomes = []
    for i in range(games): outcomes.append(run_game(test_object, model, 400, canvas, cmd_print=False))

    print("white: {0}, black: {1}".format(outcomes.count("white wins"), outcomes.count("black_wins")))
    root.mainloop()
compare("chess/Outputs/networks_Gen_40.p")