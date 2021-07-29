import numpy as np

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

# Create new network with shape (3, 5, 3)
# net1 = Network(shape=(3, 5, 3))
# net1.new()

# Return network weights then biases
# print(net1.weights)
# print(net1.biases)

# Calculate with inputs [0, 1, 1]
# print(net1.calculate(np.array([0, 1, 1])))
