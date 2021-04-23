import torch

class SLP(torch.nn.Module):
    '''
    Single perceptron, neurona de una sola capa para aproximar funciones.
    '''

    def __init__(self, input_shape, output_shape, device = torch.device("cpu")):
        '''
        :param input_shape: forma de los datos de la entrada
        :param output_shape: forma de los datos de salida
        :param device: el dispositivo cpu o gpu
        '''
        super(SLP, self).__init__()
        self.device = device
        self.input_shape = input_shape[0]
        self.hidden_shape = 40
        self.linear1 = torch.nn.Linear(self.input_shape, self.hidden_shape) 
        self.out = torch.nn.Linear(self.hidden_shape, output_shape)
    
    def forward(self, x):
        x = torch.from_numpy(x).float().to(self.device)
        x = torch.nn.functional.relu(self.linear1(x)) # funcion de activacion RELU
        x = self.out(x)
        return x