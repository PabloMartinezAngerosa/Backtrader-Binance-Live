import torch

class momentum_classification_neuralnetworks:
    def __init__(self):
        pass



def activation(x):
    ''' Sigmoid activation function
    Arguments
    ------------
    x: torch.tensor
    '''
    return 1/(1+ torch.exp(-x))

# fija la semilla aleatoria, asi las cosas son replicables
torch.manual_seed(7)
# normal distribution one row and 5 columns
features = torch.randn((1,5))

weights = torch.randn_like(features)

bias = torch.randn((1,1))

y = activation(torch.sum(features*weights + bias)) # tensor(0.4034)