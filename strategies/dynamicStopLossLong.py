# #!/usr/bin/env python3

import backtrader as bt

from config import ENV, PRODUCTION
from strategies.base import StrategyBase


class DynamicStopLossLong(StrategyBase):

    # Moving average parameters
    # params = (('pfast',20),('pslow',50),)

    def __init__(self):
        StrategyBase.__init__(self)

        self.log("Using Dynamic Stop Loss Long strategy")
        self.lendata1 = 0
        self.order = None
        self.name = "DynamicStopLossLong"

        self.indicators_ready = False
        # Cuanto permite correrse de la estimacion
        # antes de ejecutar el trade.
        self.delta_stop_loss_low = 15 
        self.delta_stop_loss_high = 15  
        self.ganancia_minima_estimada = 100

        self.hit_high_prediction = False
        self.stop_loss_low_active = False
        self.stop_loss_low = 0.0
        self.active_low_prediction = 0.0
        self.stop_loss_high_active = False
        self.stop_loss_high = 0.0
        self.active_high_prediction = 0.0
        self.orderActive  = False

    def update_stop_loss_high(self, actual_price):
        '''
        Busca el indicador mayor con las bandas y el stop loss.
        Si encuentra actualiza los valores
        '''
        # los indicadores estan de mayor  a menor
        # se busca el valor mas grande
        for high_estimation in range(self.ensambleIndicators.indicatorsHigh):
            cota_superior = high_estimation + self.delta_stop_loss_low
            cota_inferior = high_estimation - self.delta_stop_loss_low
            if (actual_price > cota_inferior and actual_price < cota_superior):
                self.stop_loss_high_active = True
                #TODO con la estimacion?
                self.active_high_prediction =  actual_price - self.delta_stop_loss_high
                self.active_high_prediction = high_estimation
                return True
        return False

    def update_stop_loss_low(self, actual_price):
        '''
        Busca el indicador menor con las bandas y el stop loss.
        Si encuentra actualiza los valores
        '''
        # los indicadores estan de menor a mayor
        # se busca el valor mas chico
        for low_estimation in range(self.ensambleIndicators.indicatorsLow):
            cota_superior = low_estimation + self.delta_stop_loss_low
            cota_inferior = low_estimation - self.delta_stop_loss_low
            if (actual_price > cota_inferior and actual_price < cota_superior):
                self.stop_loss_low_active = True
                #TODO con la estimacion?
                self.stop_loss_low =  actual_price + self.delta_stop_loss_low
                self.active_low_prediction = low_estimation
                return True
        return False


    def next(self):
        # if self.status != "LIVE" and ENV == PRODUCTION:  # waiting for live status in production
        #     return

        if self.order:  # waiting for pending order
            return

        actual_price  = self.datas[0].close[0]
        self.log('Actual Price: %.3f %% '  % actual_price)
        
        # si estan listos los indicadores
        if(self.indicators_ready):
            # si no esta activa busca low
            if (!self.orderActive):
                # busca el stop loss low minimo y actualiza valores
                self.update_stop_loss_low(actual_price)
                # si  llego a un minimo en alguna instancia
                if(self.stop_loss_low_active):
                    delta_price = actual_price - self.stop_loss_low
                    if (delta_price >= 0):
                        # se paso del stop loss ejecuta orden!
                        if (self.hit_high_prediction == False):
                            # ejecuta si la peor estimacion supera el minimo estimado de ganancia
                            min_estimation = min(self.ensambleIndicators.indicatorsHigh)
                            if (min_estimation>= self.ganancia_minima_estimada):
                                print("Ejecuta orden compra Buy!")
                            else:
                                print("Llego a minimo sin high, pero no ejecuta porque no supera estimacion de ganancia minima")
                            self.orderActive = True
                        else:
                            print("Llego a un minimo y no ejecuta porque toco high primero")
            # orden activa busca  high
            else :
                # busca el stop loss high maximo y actualiza valores
                self.update_stop_loss_high(actual_price)
                # si  llego a un minimo en alguna instancia
                if(self.stop_loss_high_active):
                    delta_price = actual_price - self.stop_loss_high
                    if (delta_price <= 0):
                        # se paso del stop loss high ejecuta orden!
                        print("Ejecuta orden venta Sell!")
            
   

        
        
        
        if len(self.data1.low) > self.lendata1:
            # update stategy indicators 
            self.updateIndicatorsEnsambleLinearModels(self.data1)
            self.indicators_ready = True
            print("New Indicators Ready!")


