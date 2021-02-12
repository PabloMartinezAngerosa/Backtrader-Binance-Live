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
        self.lagsReady = False
        
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
        self.stop_loss_low = 0
        self.active_low_prediction = 0
        self.stop_loss_high_active = False
        self.stop_loss_high = 0
        self.active_high_prediction = 0
        self.orderActive  = False

        self.jsonParser.add_strategy_name(self.name)

    def update_stop_loss_high(self, actual_price):
        '''
        Busca el indicador mayor con las bandas y el stop loss.
        Si encuentra actualiza los valores
        '''
        # los indicadores estan de mayor  a menor
        # se busca el valor mas grande
        print("busca los hig")
        print(self.ensambleIndicators.indicatorsHigh)
        
        for high_estimation in self.ensambleIndicators.indicatorsHigh:
            print(self.delta_stop_loss_low)
            cota_superior = high_estimation + self.delta_stop_loss_low
            print(cota_superior)
            cota_inferior = high_estimation - self.delta_stop_loss_low
            if (actual_price > cota_inferior and actual_price < cota_superior):
                self.stop_loss_high_active = True
                #TODO con la estimacion?
                self.active_high_prediction =  actual_price - self.delta_stop_loss_high
                self.active_high_prediction = high_estimation
                print("Toca estimador high")
                return True
        print("No toca estimador high")
        return False

    def update_stop_loss_low(self, actual_price):
        '''
        Busca el indicador menor con las bandas y el stop loss.
        Si encuentra actualiza los valores
        '''
        # los indicadores estan de menor a mayor
        # se busca el valor mas chico
        for low_estimation in self.ensambleIndicators.indicatorsLow:
            cota_superior = low_estimation + self.delta_stop_loss_low
            cota_inferior = low_estimation - self.delta_stop_loss_low
            if (actual_price > cota_inferior and actual_price < cota_superior):
                self.stop_loss_low_active = True
                #TODO con la estimacion?
                self.stop_loss_low =  actual_price + self.delta_stop_loss_low
                self.active_low_prediction = low_estimation
                print("Toca estiamdor low")
                return True
        print("No toca estimador low")
        return False


    def next(self):
        # if self.status != "LIVE" and ENV == PRODUCTION:  # waiting for live status in production
        #     return
        actual_price  = self.datas[0].close[0]
        self.jsonParser.addTick(self.datetime[0], actual_price)
        if self.order:  # waiting for pending order
            return

        self.log('Actual Price: %.3f %% '  % actual_price)
        
        # si estan listos los indicadores
        if(self.indicators_ready):
            print("Indicadores ready")
            # busca el stop loss high maximo y actualiza valores
            self.update_stop_loss_high(actual_price)
            # si no esta activa busca low
            if (self.orderActive == False):
                print("Orden no activa")
                # busca el stop loss low minimo y actualiza valores
                self.update_stop_loss_low(actual_price)
                print("Busca entre bandas")
                # si  llego a un minimo en alguna instancia
                if(self.stop_loss_low_active):
                    print("Hay una banda activa")
                    delta_price = actual_price - self.stop_loss_low
                    print(delta_price)
                    if (delta_price >= 0):
                        # se paso del stop loss ejecuta orden!
                        if (self.hit_high_prediction == False):
                            # ejecuta si la peor estimacion supera el minimo estimado de ganancia
                            min_estimation = min(self.ensambleIndicators.indicatorsHigh)
                            ganancia_estimada = min_estimation - actual_price
                            if (ganancia_estimada >= self.ganancia_minima_estimada):
                                print("Ejecuta orden compra Buy!")
                            else:
                                print("Llego a minimo sin high, pero no ejecuta porque no supera estimacion de ganancia minima")
                            self.orderActive = True
                        else:
                            print("Llego a un minimo y no ejecuta porque toco high primero")
            # orden activa busca  high
            else :
                # si  llego a un minimo en alguna instancia
                if(self.stop_loss_high_active):
                    delta_price = actual_price - self.stop_loss_high
                    if (delta_price <= 0):
                        # se paso del stop loss high ejecuta orden!
                        self.orderActive == False
                        print("Ejecuta orden venta Sell!")
        
        if len(self.data1.low) > self.lendata1:
            self.lendata1 += 1

            print("Cada cambio de Vela de 30 min")
            print(self.data1.low[0])
            
            low  = self.datas[1].low[0]
            high = self.datas[1].high[0]
            self.log('Low 1 min tick : %.3f %% '  % low)
            #self.log('High 1 min tick : %.3f %% '  % high)
            #self.log('Low data1: %.3f %% '  % float(self.data1.low[0]))
            self.log('Low -1 data1: %.3f %% '  % float(self.data1.low[-1]))

            # en produccion ya tiene los datos cargados con historial
            # llama a buscar los indicadores ya estan cargados los lags.
            if ENV == PRODUCTION:
                self.lagsReady = True
            else:
                ## si son 20 frames en la ventana de analisis, necesita al menos 21 para hacer la prediccion. 
                if (self.lendata1>self.ensambleIndicatorsLengthFrames):
                    self.lagsReady = True
            
            if (self.lagsReady):
                print("Ready para mandar datos!")
                #print(len(self.data1.low))
                self.updateIndicatorsEnsambleLinearModels(self.data1)
                self.indicators_ready = True
                print("New Indicators Ready!")
        


