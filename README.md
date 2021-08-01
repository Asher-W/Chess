# Chess

## Description

The goal of this project is to make some AI that is at least somewhat good at chess.

### How it learns

This AI learns via a genetic algorithm meaning it simulates multiple generations where the best networks get to pass on their weights and biases to the next generation.

### Network structure

Each network consists of 769 input nodes, 5 1000 node hidden layers, and 4160 output nodes.

There are 769 input nodes because there are 12 different pieces times 64 squares on a chessboard plus one node to denote whether it's playing for black or white.

There are 4160 output nodes because there are 64 starting positions times 64 end positions plus 64 nodes for promotion (16 different moves times 4 different pieces to turn into).

The 5 hidden layers of 1000 nodes have no logic behind them. We just thought that was a good number of nodes and layers.
