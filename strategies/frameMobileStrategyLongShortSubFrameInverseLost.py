# #!/usr/bin/env python3

import backtrader as bt

from config import ENV, PRODUCTION
from strategies.baseSubFrame import StrategyBase
from config import ENV, PRODUCTION, STRATEGY, TESTING_PRODUCTION, LIVE, UPDATE_PARAMS_FUERZA_BRUTA

'''

Primera version:
   * ventanas mobiles con largo dinamico por settings. 
   * opera cada 1 minuto y con filtros. 
   * mide media de diferencia high-low de multiples ventanas
   * se ajusta automaticamente a nuevos tiempos de ventanas que coinicidan con la media high-low buscada
   * mantiene estadistica de aciertors y fail
   * mantiene estadistica de balance
   * mantiene info de operaciones 
   * mantiene informacion del estado de actividad de la estrategia por si hay reinicio
   * matiene RMSE de los estimadores ( debe funcionar multiple por distintas velas y ajustarse dinamico )
   * subida/bajada acrecentada
   * high/low with succes estimation
   * estrategia de saltos shorts en velas de 15 min y pre-limit
   * mantiene estadistica de acierto de las distintas estrategias
   * UI relacionada muestra solo 1 timeline entero y las estimaciones son dinamicas a las operaciones. 
   Esta exagerada para ir inversa y perder.
   Se saca los filotrs de minima proyeccion de ganancias ysi toco antes touch.
   Se puede sacar tambien el filtro de aceleracion.

'''
class FrameMobileStrategyLongShortSubFrameInverseLost(StrategyBase):

    # Moving average parameters
    # params = (('pfast',20),('pslow',50),)

    def __init__(self, index, parent = None):
        StrategyBase.__init__(self, index=index)

        self.indicators_ready = False
        self.log("Using FrameMobileStrategyLongShortSubFrameInverseLost strategy index " + str(index))
        self.lendata1 = 0
        self.lagsReady = False
        self.ensambleIndicatorsLags = STRATEGY.get("lags")
        self.ensambleIndicatorsLengthFrames = STRATEGY.get("length_frames")
        self.candle_min = 15*16
        self.is_order_long = False
        self.is_order_short = False
        
        #self.dataclose = self.datas[0].close
        self.order = None
        self.len_frames = 0
        self.name = "FrameMobileStrategyLongShortSubFrame" + str(index)
        self.index = index
        # Instantiate moving averages
        # self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0], 
        #                 period=self.params.pslow)
        # self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0], 
        #                 period=self.params.pfast)
        
        # dynamic RMSE history estimator
        # TODO todos estos numeros se tienen que ajustar automaticamente con el dela low high.
        self.RMSE_high = 50
        self.RMSE_low = 30
        self.delta_aceleration_low = 30
        
        self.min_high_prediction =  300 

        self.parent = parent
        self.long_price = 0
        self.long_profit = 0
        self.long_stop_loss = 0
        self.short_price = 0
        self.short_profit = 0
        self.short_stop_loss = 0
        self.mean_filter_ticks = []
        self.mean_filter_lag = 5
        self.total_succes_long = 0
        self.total_fial_long = 0
        # ticks son cada 1 min aprox
        self.max_ticks = self.candle_min * 0.45 
        self.refresh()
    
    def delta_high_mean_3_succes(self, actual_price):
        high_media_3 = self.ensambleIndicators.mediaEstimadorHigh_iterada3
        if high_media_3 - actual_price > self.min_high_prediction:
            return True
        return True
    
    def refresh(self):
        self.filter_ready = False 
        self.total_ticks = 0
        #self.is_order = False
        self.touch_high_media_iterada_3 = False
        self.touch_media_low_iterada_3 = False
        self.first_touch_filter = 0
        self.delta_aceleration = False
        self.trade_made = False
        self.touch_low_media_iterada_3_short = False
        self.touch_media_high_iterada_3_short = False
        self.first_touch_filter_short = 0
        self.delta_aceleration_short = False
    
    def create_filter_mean(self, filter_tikcs, date):
        sum = 0
        for tick in filter_tikcs:
            sum = sum + tick["value"]
        mean = sum / self.mean_filter_lag
        return {"value":mean,"date":date}
    
    def is_touch_high_media_iterada_3(self, actual_price):
        high_media_3 = self.ensambleIndicators.mediaEstimadorHigh_iterada3
        if actual_price >= high_media_3 - self.RMSE_high:
            self.touch_high_media_iterada_3 = True
    
    def is_touch_low_media_iterada_3(self, actual_price, filter_price):
        low_media_3 = self.ensambleIndicators.mediaEstimadorLow_iterada3
        if actual_price >= (low_media_3 - self.RMSE_low) and actual_price <= low_media_3 + self.RMSE_low:
            if self.touch_media_low_iterada_3 == False:
                self.first_touch_filter = filter_price
            self.touch_media_low_iterada_3 = True
            #self.log("Toco  media low itereada 3  en price {} ".format(actual_price),  to_ui = True, date = self.datetime[0])
    
    def is_delta_aceleration(self, actual_price):
        if actual_price - self.first_touch_filter >= self.delta_aceleration_low:
            self.delta_aceleration =  True
            #self.log("Tuvo una aceleracion despues de media iterada en  {} con delta de {}".format(actual_price, self.delta_aceleration_low),  to_ui = True, date = self.datetime[0])
        else :
            self.delta_aceleration = False
    
    def is_touch_low_media_iterada_3_short(self, actual_price):
        low_media_3 = self.ensambleIndicators.mediaEstimadorLow_iterada3
        if actual_price <= low_media_3 + self.RMSE_high:
            self.touch_low_media_iterada_3_short = True
    
    def is_touch_high_media_iterada_3_short(self, actual_price, filter_price):
        high_media_3 = self.ensambleIndicators.mediaEstimadorHigh_iterada3
        if actual_price >= (high_media_3 - self.RMSE_low) and actual_price <= high_media_3 + self.RMSE_low:
            if self.touch_media_high_iterada_3_short == False:
                self.first_touch_filter_short = filter_price
            self.touch_media_high_iterada_3_short = True
            #self.log("Toco  media high itereada 3  en price {} ".format(actual_price),  to_ui = True, date = self.datetime[0])
    
    def is_delta_aceleration_short(self, actual_price):
        if self.first_touch_filter_short - actual_price  >= self.delta_aceleration_low:
            self.delta_aceleration_short =  True
            #self.log("Tuvo una aceleracion despues de media iterada en  {} con delta de {}".format(actual_price, self.delta_aceleration_low),  to_ui = True, date = self.datetime[0])
        else :
            self.delta_aceleration_short = False
    
    def delta_low_mean_3_succes_short(self, actual_price):
        low_media_3 = self.ensambleIndicators.mediaEstimadorLow_iterada3
        if actual_price - low_media_3  > self.min_high_prediction:
            return True
        return False

    def next(self):

        if self.order:  # waiting for pending order
            return

        close  = self.datas[0].close[0]
        actual_price = close
        message = 'Close: %.3f %% '  % close
        #self.log(message + " en index " + str(self.index))
        self.jsonParser.addTick(self.datetime[0], actual_price)

        # filter
        self.mean_filter_ticks.append({"value":actual_price,"date":self.datetime[0]})
        if  len(self.mean_filter_ticks) == self.mean_filter_lag:
            self.filter_ready =  True 
            filter_price = self.create_filter_mean(self.mean_filter_ticks, self.datetime[0])
            self.jsonParser.add_average_tick(self.datetime[0], filter_price["value"])
            # clean for memory 
            self.mean_filter_ticks.pop(0)
        
        ############################################
        #           fast trading low high - LONG   #
        ############################################
        if(self.indicators_ready and self.filter_ready):
            self.total_ticks = self.total_ticks + 1 
            if self.total_ticks <= self.max_ticks and self.is_order_long == False:
                
                self.is_touch_high_media_iterada_3(actual_price)
                self.touch_high_media_iterada_3 = False
                if self.touch_high_media_iterada_3 == False:
                    if self.touch_media_low_iterada_3 == False:
                        self.is_touch_low_media_iterada_3(actual_price, filter_price["value"])
                    else:
                        if self.delta_aceleration == False:
                            # tiene que superar un delta de aceleracion    
                            self.is_delta_aceleration(filter_price["value"])
                        else:
                            if self.trade_made == False and self.delta_high_mean_3_succes(actual_price) == True:
                                if self.parent.is_order_long == False:
                                    self.parent.is_order_long = True
                                    self.is_order_long = True
                                    #self.buy_tick = self.total_ticks
                                    self.long_price = actual_price
                                    self.long_profit = actual_price * 1.0025
                                    self.long_stop_loss = actual_price * (1 - 0.015)
                                    message = "Long Buy: " + str(actual_price) + " profit objective: " + str(self.long_profit) + " stop loss " + str(self.long_stop_loss)+ " en frame " + str(self.index)
                                    self.log(message,  to_ui = True, date = self.datetime[0], send_telegram=True)
                                    self.jsonParser.set_subida_estrepitosa(1, self.total_ticks)

            if self.is_order_long == True:
                if actual_price >= self.long_profit:
                    self.is_order_long = False
                    self.parent.is_order_long = False 
                    self.parent.total_succes_long = self.parent.total_succes_long + 1
                    self.parent.total_long_orders = self.parent.total_long_orders + "T" 
                    message = "Succes Long Buy: " + str(actual_price) + " total succes " + str(self.parent.total_succes_long) + " total fial " + str(self.parent.total_fial_long) + " en frame " + str(self.index)
                    self.log(message,  to_ui = True, date = self.datetime[0], send_telegram=True)
                    self.log(self.parent.total_long_orders,  to_ui = True, date = self.datetime[0], send_telegram=True)
                    self.jsonParser.set_subida_estrepitosa(1, self.total_ticks)
                if actual_price <= self.long_stop_loss:
                    self.is_order_long = False
                    self.parent.is_order_long = False
                    self.parent.total_fial_long = self.parent.total_fial_long + 1
                    self.parent.total_long_orders = self.parent.total_long_orders + "F"
                    message = "Fail Long Buy: " + str(actual_price) + " total fial " + str(self.parent.total_fial_long) + " total succes " + str(self.parent.total_succes_long) + " en frame " + str(self.index)
                    self.log(message,  to_ui = True, date = self.datetime[0], send_telegram=True)
                    self.log(self.parent.total_long_orders,  to_ui = True, date = self.datetime[0], send_telegram=True)
                    self.jsonParser.set_subida_estrepitosa(1, self.total_ticks)
            
            ############################################
            #           fast trading high low  - Short #
            ############################################
            if self.total_ticks <= self.max_ticks and self.is_order_short == False:
                self.is_touch_low_media_iterada_3_short(actual_price)
                if self.touch_low_media_iterada_3_short == False:
                    if self.touch_media_high_iterada_3_short == False:
                        self.is_touch_high_media_iterada_3_short(actual_price, filter_price["value"])
                    else:
                        if self.delta_aceleration_short == False:
                            self.is_delta_aceleration_short(filter_price["value"])  
                        else:
                            if  self.trade_made == False and self.delta_low_mean_3_succes_short(actual_price) == True:
                                if self.parent.is_order_short == False:   
                                    self.parent.is_order_short = True
                                    self.is_order_short = True
                                    #self.buy_tick = self.total_ticks
                                    self.short_price = actual_price
                                    self.short_profit = actual_price * (1 - 0.0025)
                                    self.short_stop_loss = actual_price * (1.015) 
                                    message = "Short Sell: " + str(actual_price) + " profit objective: " + str(self.short_profit) + " stop loss " + str(self.short_stop_loss)+ " en frame " + str(self.index)
                                    self.log(message,  to_ui = True, date = self.datetime[0], send_telegram=True)
                                    self.jsonParser.set_subida_estrepitosa(1, self.total_ticks) 
            
            if self.is_order_short == True:
                if actual_price <= self.short_profit:
                    self.is_order_short = False
                    self.parent.is_order_short = False 
                    self.parent.total_succes_short = self.parent.total_succes_short + 1
                    self.parent.total_short_orders = self.parent.total_short_orders + "T"
                    message = "Succes Short Sell: " + str(actual_price) + " total succes " + str(self.parent.total_succes_short) + " total fail " + str(self.parent.total_fial_short)+ " en frame " + str(self.index)
                    self.log(message,  to_ui = True, date = self.datetime[0], send_telegram=True)
                    self.log(self.parent.total_short_orders,  to_ui = True, date = self.datetime[0], send_telegram=True)
                    self.jsonParser.set_subida_estrepitosa(1, self.total_ticks)
                if actual_price >= self.short_stop_loss:
                    self.is_order_short = False
                    self.parent.is_order_short = False
                    self.parent.total_fial_short = self.parent.total_fial_short + 1
                    self.parent.total_short_orders = self.parent.total_short_orders + "F"
                    message = "Fail Short Sell: " + str(actual_price) + " total fail " + str(self.parent.total_fial_short)+ " total succes " + str(self.parent.total_succes_short) + "  en frame " + str(self.index)
                    self.log(message,  to_ui = True, date = self.datetime[0], send_telegram=True)
                    self.log(self.parent.total_short_orders,  to_ui = True, date = self.datetime[0], send_telegram=True)
                    self.jsonParser.set_subida_estrepitosa(1, self.total_ticks) 

                        

        if len(self.data1.low) > self.lendata1:
            self.lendata1 += 1
            #print("Cada cambio de Vela en index " + str(self.index))
            
            low  = self.datas[1].low[0]
            high = self.datas[1].high[0]
            #self.log('Low 1 min tick : %.3f %% '  % low)
            #self.log('High 1 min tick : %.3f %% '  % high)
            #self.log('Low data1: %.3f %% '  % float(self.data1.low[0]))
            #self.log('Low -1 data1: %.3f %% '  % float(self.data1.low[-1]))

            # en produccion ya tiene los datos cargados con historial
            # llama a buscar los indicadores ya estan cargados los lags.
            if ENV == PRODUCTION:
                self.lagsReady = True
            else:
                # si son 20 frames en la ventana de analisis, necesita al menos 21 para hacer la prediccion. 
                # en este caso, necesita completar los subframes necesarios para una ventana. 
                # ejemplo 4 hs. cada 16 de 15 minutos cuenta 1 de 4 horas. 
                if ( self.lendata1 >self.ensambleIndicatorsLengthFrames):
                    self.lagsReady = True
            
            if (self.lagsReady):
                #print("Ready para mandar datos cada 15 minutos 4 horas!")
                #print(len(self.data1.low))
                self.updateIndicatorsEnsambleLinearModels()
                self.indicators_ready = True
                #print("New Indicators Ready!")
                self.refresh()


        # Check if we are in the market
        # if not self.position:
        #     # We are not in the market, look for a signal to OPEN trades
            
        #     #If the 20 SMA is above the 50 SMA
        #     if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] < self.slow_sma[-1]:
        #         self.log(f'BUY CREATE {self.dataclose[0]:2f}')
        #         # Keep track of the created order to avoid a 2nd order
        #         self.order = self.buy()
        #     #Otherwise if the 20 SMA is below the 50 SMA   
        #     elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
        #         self.log(f'SELL CREATE {self.dataclose[0]:2f}')
        #         # Keep track of the created order to avoid a 2nd order
        #         self.order = self.sell()
        # else:
        #     # We are already in the market, look for a signal to CLOSE trades
        #     if len(self) >= (self.bar_executed + 5):
        #         self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
        #         self.order = self.close()

