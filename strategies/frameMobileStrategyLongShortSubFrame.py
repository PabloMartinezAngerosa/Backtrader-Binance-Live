# #!/usr/bin/env python3

import backtrader as bt
import datetime
import pandas as pd

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

'''
class FrameMobileStrategyLongShortSubFrame(StrategyBase):

    # Moving average parameters
    # params = (('pfast',20),('pslow',50),)

    def __init__(self, index, parent = None):
        StrategyBase.__init__(self, index=index)

        self.indicators_ready = False
        self.log("Using FrameMobileStrategyLongShortSubFrame strategy index " + str(index))
        self.lendata1 = 0
        self.lagsReady = False
        self.ensambleIndicatorsLags = STRATEGY.get("lags")
        self.ensambleIndicatorsLengthFrames = STRATEGY.get("length_frames")
        self.ponderador = 1 # original 4 hs x3 = 12 horas
        self.candle_min = 15*4
        self.is_order_long = False
        self.is_order_short = False
        self.action_ready = False 
        self.individual_orders = ""
        self.long_ticks_order = 0
        
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
        self.RMSE_high = 80*self.ponderador
        self.RMSE_low = 80*self.ponderador
        self.delta_aceleration_low = 30*self.ponderador
        
        self.min_high_prediction =  300*self.ponderador 

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
        self.max_ticks = self.candle_min * 0.6
        self.actual_month = 0
        self.refresh()
    
    def delta_high_mean_3_succes(self, actual_price):
        high_media_3 = self.ensambleIndicators.mediaEstimadorHigh_iterada3
        if high_media_3 - actual_price > self.min_high_prediction:
            return True
        return False
    
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
        self.action_ready = False
        self.action_ready_short = False
        print("Refresh!")
    
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
    
    def get_delta_mean(self):
        sum = 0
        for i in range(0,-1*self.ensambleIndicatorsLengthFrames,-1):
            sum = sum + self.datas[1].high[0] - self.datas[1].low[0]
        return sum/self.ensambleIndicatorsLengthFrames

    def get_delta_open_low(self):
        sum = 0
        for i in range(0,-1*self.ensambleIndicatorsLengthFrames,-1):
            sum = sum + self.datas[1].open[0] - self.datas[1].low[0]
        return sum/self.ensambleIndicatorsLengthFrames
    # getMartinGalaIndex("FFTTTF") = 1, ==T
    #getMartinGalaIndex("FFTTTFF") = 2 , ==T
    def getMartinGalaIndex( self, history_operations):
        for i in range(len(history_operations)):
            if history_operations[len(history_operations)-1-i] == "F":
                return i
        if history_operations == "":
            return 0
        else:
            return (i + 1)


    def next(self):

        if self.order:  # waiting for pending order
            return

        close  = self.datas[0].close[0]
        low = self.datas[0].low[0]
        high = self.datas[0].high[0]

        actual_price = close
        message = 'Close: %.3f %% '  % close
        #self.log(message + " en index " + str(self.index))
        self.jsonParser.addTick(self.datetime[0], actual_price)
        
        # imprime por meses 
        timestamp = bt.num2date(self.datetime[0])
        if timestamp.day != self.parent.last_day:
            self.parent.last_day = timestamp.day
            self.parent.total_orders += "-"
        if timestamp.month != self.actual_month:
            self.actual_month = timestamp.month
            self.parent.total_short_orders += str(timestamp.month)
            self.parent.total_long_orders += str(timestamp.month)
        
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
            if self.total_ticks <= self.max_ticks and self.is_order_long == False and self.action_ready == False:
                
                self.is_touch_high_media_iterada_3(actual_price)
                if self.touch_high_media_iterada_3 == False:
                    if self.touch_media_low_iterada_3 == False:
                        self.is_touch_low_media_iterada_3(actual_price, filter_price["value"])
                    else:
                        if self.delta_aceleration == False:
                            # tiene que superar un delta de aceleracion    
                            self.is_delta_aceleration(filter_price["value"])
                        else:
                            if self.trade_made == False and self.delta_high_mean_3_succes(actual_price) == True:
                                if self.parent.is_order_long == False and self.parent.is_order_short == False:
                                    self.parent.is_order_long = True
                                    self.parent.is_order_short = True
                                    self.is_order_long = True
                                    #self.buy_tick = self.total_ticks
                                    self.long_price = actual_price
                                    self.long_cost = actual_price * (1 + 0.012)
                                    #self.buffer_price_long = actual_price
                                    self.long_profit = actual_price * (1 + 0.03)
                                    #self.long_profit = actual_price + self.get_delta_mean()
                                    self.long_stop_loss = actual_price * (1 - 0.02)
                                    #self.long_stop_loss = actual_price - self.get_delta_open_low()
                                    self.long_ticks_order = -1
                                    message = "Long Buy: " + str(actual_price) + " profit objective: " + str(self.long_profit) + " - delta high-min: " + str(self.get_delta_mean())  + " stop loss " + str(self.long_stop_loss) + " delta open-low"+ str(self.get_delta_open_low()) +  "en frame " + str(self.index)
                                    self.log(message,  to_ui = True, date = self.datetime[0], send_telegram=True)
                                    self.jsonParser.set_subida_estrepitosa(1, self.total_ticks)

            if self.is_order_long == True and self.action_ready == False:
                self.long_ticks_order = self.long_ticks_order + 1
                #if self.long_ticks_order < 4:
                #    if actual_price < self.long_price:
                #        self.is_order_long = False
                #        #self.buffer_price_long = actual_price
                #        self.parent.is_order_long = False
                #        print("Saved fail!")
                #    else:
                #        if self.long_ticks_order == 3:
                #            # new limit stop loss
                #            print("change stop loss")
                #            self.long_stop_loss = actual_price * (1 - 0.004)
                #            self.long_profit = actual_price * 1.004
                #            # porcentaje q en realidad pierdo
                #            # actualiza long price al verdadero
                #            self.long_price = actual_price
                #else:
                if self.long_ticks_order > 0:
                    if self.long_ticks_order >= 5900  and self.is_order_long == True:
                        if actual_price > self.long_price:
                            self.is_order_long = False
                            self.parent.is_order_long = False 
                            self.action_ready = True
                            profit_long_succes = (actual_price/self.long_price)-1
                            self.parent.long_real_profit.append(profit_long_succes)
                            self.log(sum(self.parent.long_real_profit)/len(self.parent.long_real_profit),  to_ui = True, date = self.datetime[0], send_telegram=True)
                            self.parent.total_long_orders = self.parent.total_long_orders + "t"
                            print(self.parent.total_long_orders)
                            print("asdLongEq!")
                        else:
                            profit_long_lost = 1 - (actual_price/self.long_price)
                            self.parent.long_real_lost.append(profit_long_lost)
                            self.is_order_long = False
                            self.parent.is_order_long = False 
                            self.action_ready = True
                            self.log(sum(self.parent.long_real_lost)/len(self.parent.long_real_lost),  to_ui = True, date = self.datetime[0], send_telegram=True)
                            self.parent.total_long_orders = self.parent.total_long_orders + "f"
                            print("asdLongost!")
                            print(self.parent.total_long_orders)
                        

                    if high >= self.long_profit and self.is_order_long == True:
                        
                        self.parent.long_ticks_succes_active_order.append(self.long_ticks_order)
                        
                        # con martin gala toma en cuenta todos los F y T. hace martin gala para aumentar los T
   
                        index_martin_gala = self.getMartinGalaIndex(self.parent.total_long_orders)
                        #index_martin_gala = 0
                        capital_to = 0
                        if self.parent.acum_capital_martingala >= 100* 2**index_martin_gala:
                            capital_to = 100* 2**index_martin_gala
                        else:
                            capital_to = self.parent.acum_capital_martingala
                        #profit = profit_long_succes * capital_to * 10 + ((0.8*capital_to)/100)
                        self.parent.total_long_orders_filtered += "T"
                        #self.parent.acum_capital_martingala -= profit
                        #message = "T Long Buy: " + self.parent.total_long_orders_filtered + " total capital " + str(self.parent.acum_capital_martingala) + " index mgl  " + str(index_martin_gala) + " ganancia " + str(profit) + " capital to " + str(capital_to)
                        #self.log(message,  to_ui = True, date = self.datetime[0], send_telegram=True)

                        self.is_order_long = False
                        self.parent.is_order_long = False 
                        self.parent.is_order_short = False
                        self.action_ready = True
                        self.parent.total_succes_long = self.parent.total_succes_long + 1
                        self.parent.total_long_orders = self.parent.total_long_orders + "T" 
                        self.parent.total_orders += "T"
                        print("total: " + self.parent.total_orders)
                        self.individual_orders += "T"
                        message = "Individual orders index " + str(self.index) + " - " + self.individual_orders
                        self.log(message,  to_ui = True, date = self.datetime[0], send_telegram=True)
                        message = "Succes Long Buy: " + str(actual_price) + " total succes " + str(self.parent.total_succes_long) + " total fial " + str(self.parent.total_fial_long) + " en frame " + str(self.index)
                        self.log(message,  to_ui = True, date = self.datetime[0], send_telegram=True)
                        self.log(self.parent.total_long_orders,  to_ui = True, date = self.datetime[0], send_telegram=True)
                        #self.log(self.parent.long_ticks_succes_active_order,  to_ui = True, date = self.datetime[0], send_telegram=True)
                        
                        self.jsonParser.set_subida_estrepitosa(1, self.total_ticks)
                    if low <= self.long_stop_loss and self.is_order_long == True:
                        
                        self.parent.long_ticks_fail_active_order.append(self.long_ticks_order)

                        # con martin gala real

                        index_martin_gala = self.getMartinGalaIndex(self.parent.total_long_orders)
                        #index_martin_gala = 0
                        capital_to = 0
                        if self.parent.acum_capital_martingala >= 100* 2**index_martin_gala:
                            capital_to = 100* 2**index_martin_gala
                        else:
                            capital_to = self.parent.acum_capital_martingala
                        #profit = profit_long_lost * capital_to * 10 - ((0.8*capital_to)/100)
                        #self.parent.acum_capital_martingala += profit
                        self.parent.total_long_orders_filtered += "F"
                        #message = "F Long Buy: " + self.parent.total_long_orders_filtered + " total capital " + str(self.parent.acum_capital_martingala) + " index mgl  " + str(index_martin_gala) + " ganancia " + str(profit) + " capital to " + str(capital_to)
                        #self.log(message,  to_ui = True, date = self.datetime[0], send_telegram=True)

                        self.is_order_long = False
                        self.parent.is_order_long = False
                        self.parent.is_order_short = False
                        self.action_ready = True 
                        self.parent.total_fial_long = self.parent.total_fial_long + 1
                        self.individual_orders += "F"
                        message = "Individual orders index " + str(self.index) + " - " + self.individual_orders
                        self.log(message,  to_ui = True, date = self.datetime[0], send_telegram=True)
                        self.parent.total_long_orders = self.parent.total_long_orders + "F"
                        self.parent.total_orders += "F"
                        print("total: " + self.parent.total_orders)
                        message = "Fail Long Buy: " + str(actual_price) + " total fial " + str(self.parent.total_fial_long) + " total succes " + str(self.parent.total_succes_long) + " en frame " + str(self.index)
                        self.log(message,  to_ui = True, date = self.datetime[0], send_telegram=True)
                        self.log(self.parent.total_long_orders,  to_ui = True, date = self.datetime[0], send_telegram=True)
                        #self.log(self.parent.long_ticks_fail_active_order,  to_ui = True, date = self.datetime[0], send_telegram=True)
                        #self.log(sum(self.parent.long_real_lost)/len(self.parent.long_real_lost),  to_ui = True, date = self.datetime[0], send_telegram=True)
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
                                if self.parent.is_order_short == False and self.parent.is_order_long == False:   
                                    self.parent.is_order_short = True
                                    self.parent.is_order_long = True
                                    self.is_order_short = True
                                    #self.buy_tick = self.total_ticks
                                    self.short_price = actual_price
                                    self.short_profit = actual_price * (1 - 0.03)
                                    self.short_stop_loss = actual_price * (1.02) 
                                    message = "Short Sell: " + str(actual_price) + " profit objective: " + str(self.short_profit) + " stop loss " + str(self.short_stop_loss)+ " en frame " + str(self.index)
                                    self.log(message,  to_ui = True, date = self.datetime[0], send_telegram=True)
                                    self.jsonParser.set_subida_estrepitosa(1, self.total_ticks) 
            
            if self.is_order_short == True:
                if actual_price <= self.short_profit:
                    self.parent.short_real_profit.append(1-(actual_price/self.short_price))
                    self.is_order_short = False
                    self.parent.is_order_short = False
                    self.parent.is_order_long = False 
                    self.parent.total_succes_short = self.parent.total_succes_short + 1
                    self.parent.total_short_orders = self.parent.total_short_orders + "T"
                    self.parent.total_orders += "T"
                    print("total: " + self.parent.total_orders)
                    self.action_ready_short = True
                    message = "Succes Short Sell: " + str(actual_price) + " total succes " + str(self.parent.total_succes_short) + " total fail " + str(self.parent.total_fial_short)+ " en frame " + str(self.index)
                    #self.log(message,  to_ui = True, date = self.datetime[0], send_telegram=True)
                    self.log(self.parent.total_short_orders,  to_ui = True, date = self.datetime[0], send_telegram=True)
                    #self.log(sum(self.parent.short_real_profit)/len(self.parent.short_real_profit),  to_ui = True, date = self.datetime[0], send_telegram=True)
                    self.jsonParser.set_subida_estrepitosa(1, self.total_ticks)
                if actual_price >= self.short_stop_loss or self.total_ticks >= 720:
                    self.parent.short_real_lost.append((actual_price/self.short_price)-1)
                    self.is_order_short = False
                    self.parent.is_order_long = False
                    self.parent.is_order_short = False
                    self.action_ready_short = True
                    self.parent.total_fial_short = self.parent.total_fial_short + 1
                    self.parent.total_short_orders = self.parent.total_short_orders + "F"
                    self.parent.total_orders += "F"
                    print("total: " + self.parent.total_orders)
                    message = "Fail Short Sell: " + str(actual_price) + " total fail " + str(self.parent.total_fial_short)+ " total succes " + str(self.parent.total_succes_short) + "  en frame " + str(self.index)
                    #self.log(sum(self.parent.short_real_lost)/len(self.parent.short_real_lost),  to_ui = True, date = self.datetime[0], send_telegram=True)
                    #self.log(message,  to_ui = True, date = self.datetime[0], send_telegram=True)
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

