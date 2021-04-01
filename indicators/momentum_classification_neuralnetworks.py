import torch
import numpy as np

import torch
import torch.nn as nn
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
#import seaborn as sns
#%matplotlib inline

'''
=====
#TODO
======

Este archivo es para practica.
Con el entrenamiento mas simple del reconocimiento de subida estrepitosa.
Tambien muestra como cargarar.
Falta buscar mas opciones de entrenamiento de la red neural.
Opciones como genera mas ejemplos artificialmente de subidas estrepitosas para igualar la cantidad de ejemplos que no son.
Si se entrena con todos los ejemplos que no son, tiende a hacer overfiting a estos porque son muchos mas.
Si se entrena con igualdad por ejemplo randomico, rinde muy bien el modelo. Pero cuando se le manda al live, 
tiene un nivel muy alto, de decir que son, cuando no. Ahora se va a probar, reducir esta opciones de una manera determinista.
Tambien sepuede probar estrategias mas complejas como Recurrent Neural Network o Convolutional Neural Network.
Igualmente parece ser, un sistema muy favorable para lograr un buen redito y buen nivel de clasificacion.

'''


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



dataset = pd.read_csv("test.csv")
print(dataset.shape)
print(dataset.head())

#dataset_subid = dataset[dataset["subida_exa"]==1]
#dataset_no_subid = dataset[dataset["subida_exa"]==0]
#dataset_no_subid = dataset_no_subid.sample(n=60)
#dataset = pd.concat([dataset_subid,dataset_no_subid])
#dataset = dataset.sample(frac=1)


numerical_columns = ['price1', 'price2', 'price3','price4', 'price5','price6','price7','price8','price9','price10','price11','price12', 'low_media',
                    'low_media_iter2', 'low_media_iter3', 'low_delta', 'high_media',
                    'high_media_iter2', 'high_media_iter3', 'high_delta']
outputs = ['subida_exa']

# convert to tensor for pytorch
numerical_data = np.stack([dataset[col].values for col in numerical_columns], 1)
numerical_data = torch.tensor(numerical_data, dtype=torch.float)

print("----------------------")
print(numerical_data.shape)
print("----------------------")


#print(numerical_data[:5])

outputs = torch.tensor(dataset[outputs].values).flatten()
#print(outputs[:5])

class Model(nn.Module):

    def __init__(self, num_numerical_cols, output_size, layers, p=0.4):
        super().__init__()
        self.embedding_dropout = nn.Dropout(p)
        self.batch_norm_num = nn.BatchNorm1d(num_numerical_cols)

        all_layers = []
        input_size = num_numerical_cols

        for i in layers:
            all_layers.append(nn.Linear(input_size, i))
            all_layers.append(nn.ReLU(inplace=True))
            all_layers.append(nn.BatchNorm1d(i))
            all_layers.append(nn.Dropout(p))
            input_size = i

        all_layers.append(nn.Linear(layers[-1], output_size))

        self.layers = nn.Sequential(*all_layers)

    def forward(self, x_numerical):
        x_numerical = self.batch_norm_num(x_numerical)
        x = self.layers(x_numerical)
        return x


''' 
--------------------------
Trainning simple solution
--------------------------

print(numerical_data.shape)
print(outputs.shape)

# divide train, test
total_records = numerical_data.shape[0]
test_records = int(total_records * .3)


numerical_train_data = numerical_data[:total_records-test_records]
numerical_test_data = numerical_data[total_records-test_records:total_records]

train_outputs = outputs[:total_records-test_records]
test_outputs = outputs[total_records-test_records:total_records]

print(len(numerical_train_data))
print(len(train_outputs))

print(len(numerical_test_data))
print(len(test_outputs))

# creating a model for prediction
class Model(nn.Module):

    def __init__(self, num_numerical_cols, output_size, layers, p=0.4):
        super().__init__()
        self.embedding_dropout = nn.Dropout(p)
        self.batch_norm_num = nn.BatchNorm1d(num_numerical_cols)

        all_layers = []
        input_size = num_numerical_cols

        for i in layers:
            all_layers.append(nn.Linear(input_size, i))
            all_layers.append(nn.ReLU(inplace=True))
            all_layers.append(nn.BatchNorm1d(i))
            all_layers.append(nn.Dropout(p))
            input_size = i

        all_layers.append(nn.Linear(layers[-1], output_size))

        self.layers = nn.Sequential(*all_layers)

    def forward(self, x_numerical):
        x_numerical = self.batch_norm_num(x_numerical)
        x = self.layers(x_numerical)
        return x


model = Model(numerical_data.shape[1], 2, [200,100,50], p=0.4)
print(model)

loss_function = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

epochs = 1100
aggregated_losses = []

for i in range(epochs):
    i += 1
    y_pred = model(numerical_train_data)
    single_loss = loss_function(y_pred, train_outputs)
    aggregated_losses.append(single_loss)

    if i%25 == 1:
        print(f'epoch: {i:3} loss: {single_loss.item():10.8f}')

    optimizer.zero_grad()
    single_loss.backward()
    optimizer.step()

print(f'epoch: {i:3} loss: {single_loss.item():10.10f}')

plt.plot(range(epochs), aggregated_losses)
plt.ylabel('Loss')
plt.xlabel('epoch')

with torch.no_grad():
    y_val = model(numerical_test_data)
    loss = loss_function(y_val, test_outputs)
print(f'Loss: {loss:.8f}')

y_val = np.argmax(y_val, axis=1)

print(confusion_matrix(test_outputs,y_val))
print(classification_report(test_outputs,y_val))
print(accuracy_score(test_outputs, y_val))

# save the model
torch.save(model.state_dict(), 'subida_estrepitosa.pth')



# para leer el modelo

'''

state_dict = torch.load('../dataset/neuralnetwork/subida_estrepitosa.pth')
model = Model(numerical_data.shape[1], 2, [200,100,50], p=0.4)
model.load_state_dict(state_dict)
loss_function = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

with torch.no_grad():
    #if the actual output is 0, the value at the index 0 should be higher than the value at index 1, and vice versa.
    y_val = model(numerical_data)
    loss = loss_function(y_val, outputs)
print(f'Loss: {loss:.8f}')

y_val = np.argmax(y_val, axis=1)

print(confusion_matrix(outputs,y_val))
print(classification_report(outputs,y_val))
print(accuracy_score(outputs, y_val))