import random
import math

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def small_val():
    return random.random() * 2 - 1

class Network:
    outputs = None

    def __init__(self, shape=[], weights=[], biases=[]):
        self.shape = shape
        self.weights = weights
        self.biases = biases

    def new(self):
        for i in range(len(self.shape) - 1):
            self.weights.append([])

            # Create biases for each node - not for inputs
            # Layer > node
            self.biases.append([small_val() for k in range(self.shape[i + 1])])
            for j in range(self.shape[i + 1]):

                # Create weights based on output layer connecting back to inputs
                # Layer > node > node connections back
                self.weights[-1].append([small_val() for k in range(self.shape[i])])
    
    def tweak(self, change_limit):

        # Tweak weights
        for i in range(len(self.weights)):
            for j in range(len(self.weights[i])):
                for k, weight in enumerate(self.weights[i][j]):
                    new_value = weight + small_val() * change_limit
                    if new_value > 1:
                        new_value = sigmoid(new_value)
                    elif new_value < -1:
                        new_value = -sigmoid(new_value)
                    self.weights[i][j][k] = new_value
        
        # Tweak biases
        for i in range(len(self.biases)):
            self.biases[i] = [bias + small_val() * change_limit for bias in self.biases[i]]


    # TESTING NEEDED
    # Run with different layers and nodes and do the math to determine if it is calculating properly            
    def calculate(self, inputs):
        
        # Make nodes
        nodes = []
        for i in self.shape:
            nodes.append([0 for j in range(i)])

        nodes[0] = inputs
        
        # Calculate
        for i, layer in enumerate(nodes[1::]):
            for j in range(len(layer)):
                list_sum = 0
                for k in range(len(self.weights[i][j])):
                    list_sum += nodes[i][k] * self.weights[i][j][k]
                nodes[i + 1][j] = list_sum + self.biases[i][j]
        
        return nodes[-1]

# Create new network with shape (3, 5, 3)
# net1 = Network(shape=(3, 5, 3))
# net1.new()

# Return network weights then biases
# print(net1.weights)
# print(net1.biases)