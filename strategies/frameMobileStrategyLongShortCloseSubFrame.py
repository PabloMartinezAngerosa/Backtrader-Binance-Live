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
class FrameMobileStrategyLongShortCloseSubFrame(StrategyBase):

    # Moving average parameters
    # params = (('pfast',20),('pslow',50),)

    def __init__(self, index, parent = None):
        StrategyBase.__init__(self, index=index)

        self.indicators_ready = False
        self.log("Using FrameMobileStrategyLongShortCloseSubFrame strategy index " + str(index))
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
        self.order_price = 0

        #self.dataclose = self.datas[0].close
        self.order = None
        self.len_frames = 0
        self.name = "FrameMobileStrategyLongShortCloseSubFrame" + str(index)
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

        self.list_capital = []

        self.make_action = False
        self.lost_all = []
        self.win_all = []
        self.action_orders = ""
        self.action_short_ready = False
        self.last_action = False
        self.to_high = False
        self.to_low = False


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
        self.action_short_ready = False
        self.to_high = False
        self.to_low = False
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

    def activate_long(self):
        self.parent.is_order_short = True
        self.parent.is_order_long = True
        self.is_order_long = True
        print("Make Long")
        self.make_action = True

    def activate_short(self):
        self.parent.is_order_short = True
        self.parent.is_order_long = True
        self.is_order_short = True
        print("Make Short")
        self.make_action = True

    def decodeToFloatList(self, encoded_list):
        string_list = encoded_list.split(",")
        list_of_floats = [float(item) for item in string_list]
        return list_of_floats

    def decode_close_long(self, open_price):
        # decode high
        # decode low
        # decode close
        if min(self.decodeToFloatList(self.ensambleIndicators.closeCombo)) > open_price + 20:
            print("UpUp!")
            return True
    
    def decode_close_short(self, open_price):
        # decode high
        # decode low
        # decode close
        if max(self.decodeToFloatList(self.ensambleIndicators.closeCombo)) < open_price - 20:
            print("DownDown!")
            return True

    def decode_high_long(self, open_price):
        # decode high
        # decode low
        # decode close
        if min(self.decodeToFloatList(self.ensambleIndicators.highCombo)) > open_price + 100:
            print("HighHigh!")
            return True

    def decode_low_short(self, open_price):
        # decode high
        # decode low
        # decode close
        if max(self.decodeToFloatList(self.ensambleIndicators.closeCombo)) < open_price - 100:
            print("LowLow!")
            return True



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
        actuate = True
        if self.is_order_long == True and self.action_ready == False and self.to_high == True and actuate == True:
            if high > self.order_price:
                profit_long_succes = (high/self.order_price)-1
                if profit_long_succes > 0.008:
                    self.is_order_long = False
                    self.parent.is_order_long = False
                    self.parent.is_order_short = False 
                    self.action_ready = True
                    profit_long_succes = 0.008
                    self.parent.long_real_profit.append(profit_long_succes)
                    self.log(sum(self.parent.long_real_profit)/len(self.parent.long_real_profit),  to_ui = True, date = self.datetime[0], send_telegram=True)
                    self.parent.total_long_orders = self.parent.total_long_orders + "T"
                    print(self.parent.total_long_orders)
                    print("asdLongEq!***")
                    #capital
                    if self.parent.capital >= 500*2**self.parent.n_1:
                        self.parent.n = self.parent.n_1
                        self.parent.n_1 += 1
                    semilla = 100*2**self.parent.n
                    fee = (semilla * 0.8)/100 
                    self.parent.capital = self.parent.capital + ( (semilla * 10)* profit_long_succes - fee )
                    self.parent.list_capital.append(self.parent.capital) 
                    print(self.parent.capital)
                    if (semilla * 10)* profit_long_succes + fee > semilla:
                        print("ALERT LOST SEMILLA COMPLETE") 
                    self.parent.continue_long = False
            else:
                profit_long_lost = 1 - (low/self.order_price)
                if profit_long_lost > 0.005:
                    profit_long_lost = 0.005
                    self.parent.long_real_lost.append(profit_long_lost)
                    self.is_order_long = False
                    self.parent.is_order_long = False 
                    self.parent.is_order_short = False 
                    self.action_ready = True
                    self.log(sum(self.parent.long_real_lost)/len(self.parent.long_real_lost),  to_ui = True, date = self.datetime[0], send_telegram=True)
                    self.parent.total_long_orders = self.parent.total_long_orders + "F"
                    print("asdLongost!***")
                    print(self.parent.total_long_orders)
                    if self.parent.capital >= 500*2**self.parent.n_1:
                        self.parent.n = self.parent.n_1
                        self.parent.n_1 += 1
                    semilla = 100*2**self.parent.n
                    fee = (semilla * 0.8)/100 
                    self.parent.capital = self.parent.capital - ( (semilla * 10)* profit_long_lost + fee ) 
                    self.parent.list_capital.append(self.parent.capital)
                    print(self.parent.capital)
                    self.parent.continue_long = True

        if self.is_order_short == True and self.action_ready == False and self.to_low == True and actuate == True:
            if low < self.order_price:
                profit_short_succes = 1 - (low/self.order_price)   
                if  profit_short_succes >= 0.008:
                    profit_short_succes = 0.008
                    self.parent.long_real_lost.append(profit_short_succes)
                    self.is_order_short = False
                    self.parent.is_order_long = False 
                    self.parent.is_order_short = False 
                    self.action_ready = True
                    self.log(sum(self.parent.long_real_lost)/len(self.parent.long_real_lost),  to_ui = True, date = self.datetime[0], send_telegram=True)
                    self.parent.total_long_orders = self.parent.total_long_orders + "T"
                    print("asdShortSucces!***")
                    print(self.parent.total_long_orders)
                    if self.parent.capital >= 500*2**self.parent.n_1:
                        self.parent.n = self.parent.n_1
                        self.parent.n_1 += 1
                    semilla = 100*2**self.parent.n
                    fee = (semilla * 0.8)/100 
                    self.parent.capital = self.parent.capital + ( (semilla * 10)* profit_short_succes - fee ) 
                    self.parent.list_capital.append(self.parent.capital)
                    print(self.parent.capital)
                    self.parent.continue_long = True
            else:
                if low > self.order_price:
                    profit_short_lost = 1 - (low/self.order_price)   
                    if  profit_short_lost >= 0.005:
                        profit_short_lost = 0.005
                        self.parent.long_real_lost.append(profit_short_lost)
                        self.is_order_short = False
                        self.parent.is_order_long = False 
                        self.parent.is_order_short = False 
                        self.action_ready = True
                        self.log(sum(self.parent.long_real_lost)/len(self.parent.long_real_lost),  to_ui = True, date = self.datetime[0], send_telegram=True)
                        self.parent.total_long_orders = self.parent.total_long_orders + "F"
                        print("asdShortLost!***")
                        print(self.parent.total_long_orders)
                        if self.parent.capital >= 500*2**self.parent.n_1:
                            self.parent.n = self.parent.n_1
                            self.parent.n_1 += 1
                        semilla = 100*2**self.parent.n
                        fee = (semilla * 0.8)/100 
                        self.parent.capital = self.parent.capital - ( (semilla * 10)* profit_short_lost + fee ) 
                        self.parent.list_capital.append(self.parent.capital)
                        print(self.parent.capital)
                        self.parent.continue_long = True    
        
        ############################################
        #           fast trading low high - LONG   #
        ############################################
        if(self.indicators_ready and self.filter_ready):
            self.total_ticks = self.total_ticks + 1 

            if self.total_ticks >= 58  and (self.is_order_short == True or self.is_order_long == True) and self.action_ready == False and self.make_action == True:
                if self.is_order_long == True:
                    if actual_price > self.order_price:
                        self.is_order_long = False
                        self.parent.is_order_long = False
                        self.parent.is_order_short = False 
                        self.action_ready = True
                        profit_long_succes = (actual_price/self.order_price)-1
                        self.parent.long_real_profit.append(profit_long_succes)
                        self.log(sum(self.parent.long_real_profit)/len(self.parent.long_real_profit),  to_ui = True, date = self.datetime[0], send_telegram=True)
                        self.parent.total_long_orders = self.parent.total_long_orders + "T"
                        print(self.parent.total_long_orders)
                        print("asdLongEq!")
                        #capital
                        if self.parent.capital >= 500*2**self.parent.n_1:
                            self.parent.n = self.parent.n_1
                            self.parent.n_1 += 1
                        semilla = 100*2**self.parent.n
                        fee = (semilla * 0.8)/100 
                        self.parent.capital = self.parent.capital + ( (semilla * 10)* profit_long_succes - fee )
                        self.parent.list_capital.append(self.parent.capital) 
                        print(self.parent.capital)
                        if (semilla * 10)* profit_long_succes + fee > semilla:
                            print("ALERT LOST SEMILLA COMPLETE") 
                        self.parent.continue_long = False
                        self.last_action = True 

                    else:
                        profit_long_lost = 1 - (actual_price/self.order_price)
                        print(profit_long_lost)
                        self.parent.long_real_lost.append(profit_long_lost)
                        self.is_order_long = False
                        self.parent.is_order_long = False 
                        self.parent.is_order_short = False 
                        self.action_ready = True
                        self.log(sum(self.parent.long_real_lost)/len(self.parent.long_real_lost),  to_ui = True, date = self.datetime[0], send_telegram=True)
                        self.parent.total_long_orders = self.parent.total_long_orders + "F"
                        print("asdLongost!")
                        print(self.parent.total_long_orders)
                        if self.parent.capital >= 500*2**self.parent.n_1:
                            self.parent.n = self.parent.n_1
                            self.parent.n_1 += 1
                        semilla = 100*2**self.parent.n
                        fee = (semilla * 0.8)/100 
                        self.parent.capital = self.parent.capital - ( (semilla * 10)* profit_long_lost + fee ) 
                        self.parent.list_capital.append(self.parent.capital)
                        print(self.parent.capital)
                        self.parent.continue_long = True
                if self.is_order_short == True:
                    if actual_price < self.order_price:
                        self.is_order_short = False
                        self.parent.is_order_long = False
                        self.parent.is_order_short = False 
                        self.action_ready = True
                        profit_short_succes = 1 - (actual_price/self.order_price)
                        self.parent.long_real_profit.append(profit_short_succes)
                        self.log(sum(self.parent.long_real_profit)/len(self.parent.long_real_profit),  to_ui = True, date = self.datetime[0], send_telegram=True)
                        self.parent.total_long_orders = self.parent.total_long_orders + "T"
                        print(self.parent.total_long_orders)
                        print("asdShortEq!")
                        #capital
                        if self.parent.capital >= 500*2**self.parent.n_1:
                            self.parent.n = self.parent.n_1
                            self.parent.n_1 += 1
                        semilla = 100*2**self.parent.n
                        fee = (semilla * 0.8)/100 
                        self.parent.capital = self.parent.capital + ( (semilla * 10)* profit_short_succes - fee )
                        self.parent.list_capital.append(self.parent.capital) 
                        print(self.parent.capital)
                        if (semilla * 10)* profit_short_succes + fee > semilla:
                            print("ALERT LOST SEMILLA COMPLETE")                         
                    else:
                        profit_short_lost =  (actual_price/self.order_price) - 1
                        print(profit_short_lost)
                        self.parent.long_real_lost.append(profit_short_lost)
                        self.is_order_long = False
                        self.parent.is_order_long = False 
                        self.parent.is_order_short = False 
                        self.action_ready = True
                        self.log(sum(self.parent.long_real_lost)/len(self.parent.long_real_lost),  to_ui = True, date = self.datetime[0], send_telegram=True)
                        self.parent.total_long_orders = self.parent.total_long_orders + "F"
                        print("asdShortLost!")
                        print(self.parent.total_long_orders)
                        if self.parent.capital >= 500*2**self.parent.n_1:
                            self.parent.n = self.parent.n_1
                            self.parent.n_1 += 1
                        semilla = 100*2**self.parent.n
                        fee = (semilla * 0.8)/100 
                        self.parent.capital = self.parent.capital - ( (semilla * 10)* profit_short_lost + fee ) 
                        self.parent.list_capital.append(self.parent.capital)
                        print(self.parent.capital)   

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

                high_predicted = self.ensambleIndicators.mediaEstimadorHigh
                low_predicted = self.ensambleIndicators.mediaEstimadorLow
                close_predicted = self.ensambleIndicators.mediaEstimadorClose

                if self.parent.is_order_short == False and self.parent.is_order_long == False:
                    self.order_price = actual_price # es el open 
                    '''
                    if self.decode_close_long(actual_price) == True:
                        print("Va en Long para el close")
                        self.activate_long()
                        self.to_high = True
                    elif self.decode_close_short(actual_price) == True:
                        print("Va en Short para el close")
                        self.activate_short()
                        self.to_low = True
                    '''
                    if actual_price - low_predicted < 200:
                        print("Va en Long para el close")
                        self.activate_long()
                        self.to_high = True
                    else:
                        print("Va en Short para el close")
                        self.activate_short()
                        self.to_low = True


                    #if self.decode_close_long(actual_price) == True: 
                    #    if close_predicted/actual_price - 1 >= 0.01:
                    #        print("Va en Long para el high")
                    #        self.activate_long()
                    #        self.to_high = False


                        #else:
                        #    print("Va en Short para el low")
                        #self.activate_short()
                        #    self.to_low = True
                    

                        #self.last_action = False
                        #self.long_profit = actual_price * (1 + 0.005)
                        #self.long_stop_loss = actual_price * (1 - 0.02)
                        #self.parent.is_order_short = True
                        #self.parent.is_order_long = True
                        #self.is_order_long = True
                        #print("Make Long")
                        #self.parent.continue_short = False
                        #self.make_action = True
                        #self.touch_high_media_iterada_3 = False
                    #elif 1 - high_predicted/actual_price >= 0.01:
                    #    print("Make Short")
                    #self.short_profit = actual_price * (1 - 0.03)
                    #self.short_stop_loss = actual_price * (1.02) 
                    #    self.parent.is_order_short = True
                    #    self.parent.is_order_long = True
                    #    self.is_order_short = True
                    #    self.parent.continue_long = False
                    #if self.parent.continue_long == True:
                    #    self.parent.is_order_short = True
                    #    self.parent.is_order_long = True
                    #    self.is_order_long = True
                    #if self.parent.continue_short == True:
                    #    self.parent.is_order_short = True
                    #    self.parent.is_order_long = True
                    #    self.is_order_short = True



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

