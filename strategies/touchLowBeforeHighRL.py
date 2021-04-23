# #!/usr/bin/env python3

import backtrader as bt

from config import ENV, PRODUCTION
from strategies.base import StrategyBase

from config import ENV, PRODUCTION, STRATEGY, TESTING_PRODUCTION, LIVE, UPDATE_PARAMS_FUERZA_BRUTA

import numpy as np
import torch
import torch.nn as nn
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

from sklearn import linear_model

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



class TouchLowBeforeHighRL(StrategyBase):

    # Moving average parameters
    # params = (('pfast',20),('pslow',50),)

    def __init__(self):
        StrategyBase.__init__(self)

        self.log("Using Touch Low Before High RL strategy")
        self.lendata1 = 0
        self.indicators_ready = False

        self.ensambleIndicatorsLags = STRATEGY.get("lags")
        self.ensambleIndicatorsLengthFrames = STRATEGY.get("length_frames")
        self.candle_min = STRATEGY.get("candle_min")
        
        #self.dataclose = self.datas[0].close
        self.order = None
        self.name = "TouchLowBeforeHighRL"
        self.ticks_to_neuralNetowkr = 12
        self.total_ticks_buffer = 6 # representa cinco para adelante, el primero es el valor final en la aceleracion 
        self.numerical_data = []
        self.total_ticks = 0
        self.total_subidas_estrpitosas = 0
        # load the previous trainned neural network
        
        # Instantiate moving averages
        # self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0], 
        #                 period=self.params.pslow)
        # self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0], 
        #                 period=self.params.pfast)
        #state_dict = torch.load('dataset/neuralnetwork/subida_estrepitosa.pth')
        # funciona con los primeros 12 ticks despues de las estimaciones
        #self.model = Model(20, 2, [200,100,50], p=0.4)
        #self.model.load_state_dict(state_dict)
        self.start_tick_aceleration_momentum = False
        self.ticks_buffer = 0
        self.ticks_aceleration_momentum_delta = []
        self.index_touch = 0 
        self.delta_buffer = 0
        
    def add_estimators_total_data(self):
        '''
        -------------------------
        numerical data expected
        -------------------------
        numerical_columns = ['price1', 'price2', 'price3','price4', 'price5','price6','price7','price8','price9','price10','price11','price12', 'low_media',
        'low_media_iter2', 'low_media_iter3', 'low_delta', 'high_media',
        'high_media_iter2', 'high_media_iter3', 'high_delta']
        '''
        # first low
        self.numerical_data.append(self.ensambleIndicators.mediaEstimadorLow)
        self.numerical_data.append(self.ensambleIndicators.mediaEstimadorLow_iterada2)
        self.numerical_data.append(self.ensambleIndicators.mediaEstimadorLow_iterada3)
        self.numerical_data.append(self.ensambleIndicators.deltaMediaOpenLow)
        # second high
        self.numerical_data.append(self.ensambleIndicators.mediaEstimadorHigh)
        self.numerical_data.append(self.ensambleIndicators.mediaEstimadorHigh_iterada2)
        self.numerical_data.append(self.ensambleIndicators.mediaEstimadorHigh_iterada3)
        self.numerical_data.append(self.ensambleIndicators.deltaMediaOpenHigh)
    
    # convierte numerical data list ino tensor
    def get_tensor_numerical_data(self):
        return torch.tensor([self.numerical_data], dtype=torch.float)
    
    def touch_low_before_high_condition(self, numerical_data):
        length = len(numerical_data)
        # si toco algun estimador high(el minimo al menos) return false
        for i in range(length):
            if numerical_data[i] >= self.ensambleIndicators.mediaEstimadorHigh_iterada3:
                return False,0
            # si toca algun estimador low (el maximo al menos)
            if numerical_data[i] <= self.ensambleIndicators.mediaEstimadorLow_iterada3:
                return True,i            
        # no toco ni high ni low
        return False,len(numerical_data) -1
            
    def aceleration_momentum_condition(self, numerical_data):
        '''
        La idea es filtrar las velas que llegan a la red neuronal, para equilibrar la respuesta de esta.
        En un entorno, donde se les mandan las subidas exaceravadas en igual condicion que 
        momentos que no son subidas exacervadas con buena representacion, la Red Neuronal responde muy bien.
        En general existe un Momentum, cuando se tocan los 3 (o 4) estimadores en un intervalo de no mas de 3 min.
        Se pueden agregar condiciones mas duras, como si toco low no entra, si no es en los primeros minutos (funciona muy bien 5 aunque no contempla algunos casos)
        o si no pasaron los cuatros estimadores (incluyendo delta high) no contempla.
        '''
        # primero busca d a uno
        # busca de a 2
        length = len(numerical_data)
        for i in range(length):
            if i%2 == 1:
                cota_superior = numerical_data[i]
                cota_inferior = numerical_data[i-1]
                if cota_superior > cota_inferior:
                    # esta primera version no utiliza delta estimator
                    # mas alto es high mean y mas bajo es high men iter 3
                    if self.ensambleIndicators.mediaEstimadorHigh_iterada3 >= cota_inferior and self.ensambleIndicators.mediaEstimadorHigh <= cota_superior:
                        self.log("Existe aceleracion de 1 delta, desd el tick " + str(i-1) + " a " + str(i),  to_ui = True, date = self.datetime[0])
                        return True, i, 1

            if i%3 == 2:
                cota_superior = numerical_data[i]
                cota_inferior = numerical_data[i-2]
                if cota_superior > cota_inferior:
                    # esta primera version no utiliza delta estimator
                    # mas alto es high mean y mas bajo es high men iter 3
                    if self.ensambleIndicators.mediaEstimadorHigh_iterada3 >= cota_inferior and self.ensambleIndicators.mediaEstimadorHigh <= cota_superior:
                        self.log("Existe aceleracion de 2 delta, desd el tick " + str(i-2) + " a " + str(i),  to_ui = True, date = self.datetime[0])
                        return True, i, 2
            if i%4 == 3:
                cota_superior = numerical_data[i]
                cota_inferior = numerical_data[i-3]
                if cota_superior > cota_inferior:
                    # esta primera version no utiliza delta estimator
                    # mas alto es high mean y mas bajo es high men iter 3
                    if self.ensambleIndicators.mediaEstimadorHigh_iterada3 >= cota_inferior and self.ensambleIndicators.mediaEstimadorHigh <= cota_superior:
                        self.log("Existe aceleracion de 3 delta, desd el tick " + str(i-3) + " a " + str(i),  to_ui = True, date = self.datetime[0])
                        return True, i, 3 
            if i%5 == 4:
                cota_superior = numerical_data[i]
                cota_inferior = numerical_data[i-4]
                if cota_superior > cota_inferior:
                    # esta primera version no utiliza delta estimator
                    # mas alto es high mean y mas bajo es high men iter 3
                    if self.ensambleIndicators.mediaEstimadorHigh_iterada3 >= cota_inferior and self.ensambleIndicators.mediaEstimadorHigh <= cota_superior:
                        self.log("Existe aceleracion de 4 delta, desd el tick " + str(i-4) + " a " + str(i),  to_ui = True, date = self.datetime[0])
                        return True, i, 4
        return False,0,0
                
    def scale_ticks(self, data):
        min_element = min(data)
        max_element = max(data)
        buffer_data = []
        for element in data:
            #y = (x – min) / (max – min)
            sacled_element = (element - min_element) / (max_element - min_element)
            buffer_data.append(sacled_element)
        return buffer_data
    
    def get_linear_regresion_data(self, data):
        Y = data
        X = []
        for i in range(len(data)):
            X.append([i])
        return X,Y


    def refresh(self):
        self.total_ticks = 0
        self.numerical_data = []
        self.start_tick_aceleration_momentum = False
        self.ticks_buffer = 0
        self.ticks_aceleration_momentum_delta = []
        self.index_touch = 0 
        self.delta_buffer = 0


    def next(self):
        # if self.status != "LIVE" and ENV == PRODUCTION:  # waiting for live status in production
        #     return

        if self.order:  # waiting for pending order
            return

        close  = self.datas[0].close[0]
        actual_price = close
        #self.log('Close: %.3f %% '  % close)
        self.jsonParser.addTick(self.datetime[0], actual_price)
        # self.log('Close: %.3f %% '  % float(self.data0.close[-1]))
        
        #  update stategy indicators 
        # self.updateIndicatorsEnsambleLinearModels(self.data0)
        if(self.indicators_ready):
            self.total_ticks = self.total_ticks + 1 
            self.numerical_data.append(actual_price)

            # solo cuando pasaron los ticks suficientes para mandar a la red neuronal
            if (self.total_ticks == self.ticks_to_neuralNetowkr):
                aceleration_momentum, self.index_touch = self.touch_low_before_high_condition(self.numerical_data)
                 
                if aceleration_momentum == True:
                    self.start_tick_aceleration_momentum = True
                    '''
                    with torch.no_grad():
                        # if the actual output is 0, the value at the index 0 should be higher than the value at index 1, and vice versa.
                        self.add_estimators_total_data()
                        tensor_numerical_data = self.get_tensor_numerical_data()
                        self.model.eval()
                        y_val = self.model(tensor_numerical_data)
                        y_val = np.argmax(y_val, axis=1)
                        if y_val == 1:
                            self.total_subidas_estrpitosas = self.total_subidas_estrpitosas + 1
                            self.jsonParser.set_subida_estrepitosa(1)
                            #print("Es subida estrepitosa")
                        else:
                            self.jsonParser.set_subida_estrepitosa(0)
                            #print("No es subida estrepitosa")
                    '''
                    self.jsonParser.set_subida_estrepitosa(1, self.index_touch)
                else:
                    self.jsonParser.set_subida_estrepitosa(0)
                    #print("No existe aceleracion!")

            '''
            if self.start_tick_aceleration_momentum == True:
                self.ticks_buffer = self.ticks_buffer + 1
                self.ticks_aceleration_momentum_delta.append(actual_price)
                if self.ticks_buffer == self.total_ticks_buffer:
                    # generate normalized data
                    #print(self.ticks_aceleration_momentum_delta)
                    scaled_ticks = self.scale_ticks(self.ticks_aceleration_momentum_delta)
                    # generate linear regression coeficients
                    reg = linear_model.LinearRegression()
                    X, Y = self.get_linear_regresion_data(scaled_ticks)
                    reg.fit(X, Y)
                    coef = reg.coef_[0]
                    intercept = reg.intercept_
                    r_squared = reg.score(X,Y)
                    self.log("El scope es " + str(coef) + " , el r cuadrado " + str(r_squared),  to_ui = True, date = self.datetime[0])
                    if coef < 0.1:
                        self.log("El scope es menor q 1, no se ejecuta la compra! ",  to_ui = True, date = self.datetime[0])
                    else:
                        last_index = len(self.ticks_aceleration_momentum_delta) - 1
                        if self.ticks_aceleration_momentum_delta[last_index] <= self.ensambleIndicators.mediaEstimadorHigh:
                            self.log("El scope es positivo, pero el ultimo valor es menor que el estimador media high. No realiza compra!",  to_ui = True, date = self.datetime[0])
                        else:
                            self.log("El scope es positivo, y el ultimo valor es mayor que el estimador media high. Realiza compra! " + str(self.ticks_aceleration_momentum_delta[last_index]) + " <" + str(self.ensambleIndicators.mediaEstimadorHigh),  to_ui = True, date = self.datetime[0])
                            #self.jsonParser.set_subida_estrepitosa_buffer(scaled_ticks, coef, intercept, r_squared, self.index_buffer, self.delta_buffer)
            '''


        
        if len(self.data1.low) > self.lendata1:
            self.lendata1 += 1
            # en produccion ya tiene los datos cargados con historial
            # llama a buscar los indicadores ya estan cargados los lags.
            if ENV == PRODUCTION:
                self.indicators_ready = True
            else:
                ## si son 20 frames en la ventana de analisis, necesita al menos 21 para hacer la prediccion. 
                if (self.lendata1>self.ensambleIndicatorsLengthFrames):
                    self.indicators_ready = True
            
            if (self.indicators_ready):
                self.updateIndicatorsEnsambleLinearModels()
                #self.indicators_ready = True
                #print("New Indicators Ready!")
                self.refresh()

