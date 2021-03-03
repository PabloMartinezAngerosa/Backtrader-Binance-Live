# #!/usr/bin/env python3

import backtrader as bt

from config import ENV, PRODUCTION, STRATEGY
from strategies.base import StrategyBase


class DynamicStopLossLong(StrategyBase):

    # Moving average parameters
    # params = (('pfast',20),('pslow',50),)

    def __init__(self):
        StrategyBase.__init__(self)

        # configuration
        self.ensambleIndicatorsLags = STRATEGY.get("lags")
        self.ensambleIndicatorsLengthFrames = STRATEGY.get("length_frames")
        self.candle_min = STRATEGY.get("candle_min")

        self.log("Using Dynamic Stop Loss Long strategy")
        self.lendata1 = 0
        self.lagsReady = False
        
        self.order = None
        self.name = "DynamicStopLossLong"

        self.actual_tick = 0
        self.mean_tick = STRATEGY.get("mean_tick_dev")
        if ENV == PRODUCTION:
            self.mean_tick = STRATEGY.get("mean_tick_prod")

        self.indicators_ready = False
        self.stoploss = 100
        self.tick_max = 0.70 # 75% de los ticks de la vela deja ejecutar
        self.max_without_action = 0.45 # porcentaje de ticks de tiempo q acepta sin ejecutar accion fuerte
        # Cuanto permite correrse de la estimacion
        # antes de ejecutar el trade.
        self.delta_stop_loss_low = 25 
        self.delta_stop_loss_high = 50
        self.delta_band_stop_loss_low = 50 
        self.ganancia_minima_estimada = 100
        self.minimum_revenue_estimation = 250

        self.stop_loss_low_active = False
        self.stop_loss_low = 0
        self.active_low_prediction = 0
        self.stop_loss_high_active = False
        self.stop_loss_high = 0
        self.active_high_prediction = 0
        self.orderActive  = False
        self.made_trade = False

        self.open_candle = 0
        self.is_first_tick = False
        self.active_ticks = 0

        self.delta_stoploss_time = 30

        self.toco_high = False

        self.jsonParser.add_strategy_name(self.name)

    def update_stop_loss_high(self, actual_price):
        '''
        Busca el indicador mayor con las bandas y el stop loss.
        Si encuentra actualiza los valores
        '''
        # los indicadores estan de mayor  a menor
        # se busca el valor mas grande
        # print("busca los hig")
        # print(self.ensambleIndicators.indicatorsHigh)
        for high_estimation in self.ensambleIndicators.indicatorsHigh:
            #cota_superior = high_estimation + self.delta_stop_loss_high
            cota_inferior = high_estimation - self.delta_stop_loss_high
            if (actual_price > cota_inferior and high_estimation >= self.open_candle) :
                self.stop_loss_high_active = True
                #TODO con la estimacion?
                if (actual_price - self.delta_stop_loss_high > self.stop_loss_high):
                    self.stop_loss_high =  actual_price - self.delta_stop_loss_high
                    self.active_high_prediction = high_estimation
                # print("Toca estimador high")
                return True
        # print("No toca estimador high")
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
            #cota_inferior = low_estimation - self.delta_stop_loss_low
            if (actual_price < cota_superior and low_estimation <= self.open_candle):
                self.stop_loss_low_active = True
                if (actual_price + self.delta_band_stop_loss_low < self.stop_loss_low):
                    self.stop_loss_low =  actual_price + self.delta_band_stop_loss_low
                    self.active_low_prediction = low_estimation
                # print("Toca estiamdor low")
                return True
        # print("No toca estimador low")
        return False

    def refresh_variables(self):
        self.stop_loss_low_active = False
        self.stop_loss_high_active = False
        self.orderActive = False
        self.is_first_tick = True
        self.active_ticks = 0
        self.made_trade = False
        self.toco_high = False
    
    def sell_order(self):
        if self.last_operation != "SELL":
            self.short()
            self.orderActive = False
            self.made_trade = True
            
    def minimum_delta_high_estimation(self, actual_price):
        ''' asume que estan ordenadas de mayor a menor 
        las estimaciones del high '''
        min_high_estimation = self.open_candle
        for index in [3,2,1,0]:
            estimation = self.ensambleIndicators.indicatorsHigh[index]
            print(estimation)
            if estimation >= min_high_estimation:
                min_high_estimation = estimation
                break 
        if min_high_estimation - actual_price >= self.ganancia_minima_estimada:
            return True
        message = "El minimo high etimado no alcanza la ganancia minima requerida de " + str(self.ganancia_minima_estimada)
        self.log(message, to_ui = True, date = self.datetime[0])
        return False

    def add_minimun_revenue(self,actual_price):
        self.ensambleIndicators.indicatorsHigh.append(actual_price + self.minimum_revenue_estimation)


    def next(self):
        # if self.status != "LIVE" and ENV == PRODUCTION:  # waiting for live status in production
        #     return
        actual_price  = self.datas[0].close[0]
        self.actual_tick = self.actual_tick + 1
        self.jsonParser.addTick(self.datetime[0], actual_price)
        
        if self.order:  # waiting for pending order
            return

        self.log('Actual Price: %.3f %% '  % actual_price)
        
        # si estan listos los indicadores
        if(self.indicators_ready and self.made_trade == False):
            if self.is_first_tick == True:
                self.is_first_tick = False
                self.open_candle = actual_price
                self.stop_loss_low = actual_price
                self.stop_loss_high = actual_price
            #print("Indicadores ready")
            # busca el stop loss high maximo y actualiza valores
            self.update_stop_loss_high(actual_price)
            # si no esta activa busca low
            if (self.orderActive == False):
                #print("Orden no activa")
                # busca el stop loss low minimo y actualiza valores
                self.update_stop_loss_low(actual_price)
                #print("Busca entre bandas")
                # si  llego a un minimo en alguna instancia
                if(self.stop_loss_low_active):
                    #print("Hay una banda activa")
                    delta_price = actual_price - self.stop_loss_low
                    print(delta_price)
                    #print(delta_price)
                    if (delta_price > 0):
                        # se paso del stop loss ejecuta orden!
                        if (self.stop_loss_high_active == False and self.minimum_delta_high_estimation(actual_price)):
                            # ejecuta si la peor estimacion supera el minimo estimado de ganancia
                            #min_estimation = min(self.ensambleIndicators.indicatorsHigh)
                            #ganancia_estimada = min_estimation - actual_price
                            #if (ganancia_estimada >= self.ganancia_minima_estimada):
                            if self.last_operation != "BUY" and  self.actual_tick < (self.mean_tick * self.tick_max):
                                self.log("Ejecuta orden compra Buy! despues de delta " + str(delta_price),  to_ui = True, date = self.datetime[0])
                                self.long()
                                self.add_minimun_revenue(actual_price)
                                #else:
                                #    print("Llego a minimo sin high, pero no ejecuta porque no supera estimacion de ganancia minima")
                                self.orderActive = True
                        else:
                            if self.toco_high == False:
                                self.log("Llego a un minimo y no ejecuta porque toco high primero",  to_ui = True, date = self.datetime[0])
                                self.toco_high = True
            # orden activa busca  high
            else :
                self.active_ticks = self.active_ticks + 1
                # si  llego a un minimo en alguna instancia
                if(self.stop_loss_high_active == True):
                    delta_price = actual_price - self.stop_loss_high
                    if (delta_price <= 0):
                        # se paso del stop loss high ejecuta orden!
                        if self.last_operation != "SELL":
                            self.log("Ejecuta orden venta Sell! despues de delta " + str(delta_price),  to_ui = True, date = self.datetime[0])
                            self.sell_order()
                # si llega al final y todavia no toco un high
                elif self.actual_tick >= (self.mean_tick - 10):
                    if self.last_operation != "SELL":
                        self.log("esta llegando close y no toco high. ejecuta venta",  to_ui = True, date = self.datetime[0])
                        self.sell_order()
                # stoploss time
                # si pasa un porcentaje de tiempo y no hay suficiente ganancia
                elif self.active_ticks >= self.mean_tick * self.max_without_action:
                    if actual_price >= (self.buy_price_close - self.delta_stoploss_time) and actual_price <=  (self.buy_price_close + self.delta_stoploss_time):
                        self.log("Stop loss time, sin action! Sell", to_ui = True, date = self.datetime[0])
                        self.sell_order()
                # stoploss si la estimacion es incorrecta y se va a la baja
                elif self.buy_price_close - actual_price  > self.stoploss:
                    self.log("Stop loss " + str(self.buy_price_close - actual_price),   to_ui = True, date = self.datetime[0])
                    self.sell_order()

                    
        
        if len(self.data1.low) > self.lendata1:
            self.lendata1 += 1
            self.actual_tick = 0

            print("Cada cambio de Vela de " + str(self.candle_min)  + " min")
            #print(self.data1.low[0])
            
            # low  = self.datas[1].low[0]
            # high = self.datas[1].high[0]
            # self.log('Low : %.3f %% '  % low)
            #self.log('High 1 min tick : %.3f %% '  % high)
            #self.log('Low data1: %.3f %% '  % float(self.data1.low[0]))
            # self.log('Low -1 data1: %.3f %% '  % float(self.data1.low[-1]))

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
                self.updateIndicatorsEnsambleLinearModels()
                self.indicators_ready = True
                self.refresh_variables()
        


