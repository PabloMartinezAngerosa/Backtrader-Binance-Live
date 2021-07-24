# #!/usr/bin/env python3
'''

Esta estraegia es un mix de fastTradingNoFeedLowHigh con allNoFee (subida acrecentada)
Se manejan proyecciones de ganancia independiente para establecer un margen ganancia en cada una independeinte.
Esto es para reducir el riesgo, muchas veces se alcanza a los objetivos en 12 hs pero por dejar mas, se baja.
Tambien se establece un margen general, que es el que finaliza los trades de las 12 hs.

'''
import backtrader as bt

from config import ENV, PRODUCTION, DEVELOPMENT
from strategies.base import StrategyBase

from config import ENV, PRODUCTION, STRATEGY, TESTING_PRODUCTION, LIVE, UPDATE_PARAMS_FUERZA_BRUTA, MULTIPLE_INSTANCE
import numpy as np
import pandas as pd

import math

class SimpleLowHighPhemexStaticLoss(StrategyBase):

    # Moving average parameters
    # params = (('pfast',20),('pslow',50),)

    def __init__(self, phemex_automation = None):
        StrategyBase.__init__(self)

        self.log("Using FastTradingNoFeeLowHigh strategy")
        self.lendata1 = 0
        self.indicators_ready = False

        self.ensambleIndicatorsLags = STRATEGY.get("lags")
        self.ensambleIndicatorsLengthFrames = STRATEGY.get("length_frames")
        self.candle_min = STRATEGY.get("candle_min")
        
        # self.acum_capital = 100 se fija en base
        self.acum_capital_acrecentada = 100
        self.acum_capital_low_high = 100
        

        self.acum_capital_previous = 100
        self.profit_history = []

        self.RMSE_low = 15 # RMSE si toca estimador low, se busca preciso
        self.min_high_prediction =  50
        self.RMSE_high = 30*3 # RMSE si toca antes algun estimador high
        self.RMSE_low_acrecentada = 10/3
        self.RMSE_high_acrecentada = 30/3
        self.delta_aceleration_low = 20
        self.delta_aceleration_low_acrecentada = 40/3
        self.max_profit_strategy = 0.012
        

        self.mean_tick = STRATEGY.get("mean_tick_dev")
        if ENV == PRODUCTION:
            self.mean_tick = STRATEGY.get("mean_tick_prod")
        

        self.set_limit_profit_objectives()

        self.max_ticks = self.mean_tick * 0.45
        self.max_ticks_acrecentada = self.mean_tick * 0.65

        self.active_no_loss_profit = False
        self.tick_buy_time = 0


        #self.dataclose = self.datas[0].close

        self.mean_filter_ticks = []
        self.mean_filter_lag = 5
        self.order = None
        self.trade_made = False
        self.trade_made_acrecentada = False
        self.name = "FastTradingNoFeeLowHigh"
        self.buy_price = 0
        self.buy_price_acrecentada = 0
        self.buy_price_actual = 0
        self.buy_price_actual_acrecentada = 0
        self.is_order = False
        self.refresh()
        self.phemex_automation = phemex_automation

        self.count_mins = 0

        self.buy_price_binance = 0


    def set_limit_profit_objectives(self):
        self.max_profit = STRATEGY.get("max_profit") * self.acum_capital
        if MULTIPLE_INSTANCE == False:
            print("max profit es " + str(self.max_profit))
        self.min_profit = STRATEGY.get("min_profit") * self.acum_capital
        if MULTIPLE_INSTANCE == False:
            print("min profit indicual es " + str(self.min_profit))
        self.continue_acrecentada_strategy = True
        self.continue_low_to_high_strategy = True

    def create_filter_mean(self, filter_tikcs, date):
        sum = 0
        for tick in filter_tikcs:
            sum = sum + tick["value"]
        mean = sum / self.mean_filter_lag
        return {"value":mean,"date":date}

    def refresh(self):
        self.total_ticks = 0
        self.touch_media_low = False
        self.touch_media_high = False
        self.touch_high_media_iterada_3 = False
        self.touch_media_low_iterada_3 = False
        self.touch_media_high_iterada_3 = False
        self.touch_low_media_iterada_3_acrecentada = False
        self.delta_aceleration = False
        self.delta_aceleration_acrecentada = False
        # self.is_order = False
        self.is_order_acrecentada = False
        #self.buy_price = 0
        #self.buy_price_acrecentada = 0
        #self.buy_price_actual = 0
        #self.buy_price_actual_acrecentada = 0
        self.filter_ready = False 
        self.active_no_loss_profit = False
        self.trade_made = False
        self.first_touch_filter = 0
        self.first_touch_filter_acrecentada = 0
        self.pre_buy = False
        self.pre_buy_acrecentada = False
        self.pre_buy_price = 0
        self.pre_sell = False
        self.pre_sell_acrecentada = False
        self.pre_sell_price = 0
        self.pre_sell_price_acrecentada = 0
    
    def is_touch_high_media_iterada_3(self, actual_price):
        high_media_3 = self.ensambleIndicators.mediaEstimadorHigh_iterada3
        if actual_price >= high_media_3 - self.RMSE_high:
            self.touch_high_media_iterada_3 = True
            #self.log("Toco high media iterada 3 en price {} con delta de {}".format(actual_price, self.RMSE_high),  to_ui = True, date = self.datetime[0])
    
    def is_touch_low_media_iterada_3_acrecentada(self, actual_price):
        #high_media_3 = self.ensambleIndicators.mediaEstimadorHigh_iterada3
        high_media_3 = self.ensambleIndicators.mediaEstimadorLow_iterada3
        #if actual_price >= high_media_3 - self.RMSE_high:
        if actual_price <= high_media_3 + self.RMSE_high_acrecentada:
            self.touch_low_media_iterada_3_acrecentada = True
            #self.log("Toco high media iterada 3 en price {} con delta de {}".format(actual_price, self.RMSE_high),  to_ui = True, date = self.datetime[0])

    def is_touch_media_low(self, actual_price):
        low_media = self.ensambleIndicators.mediaEstimadorLow_iterada3
        if actual_price <= low_media + self.RMSE_low and actual_price >= low_media - self.RMSE_low:
            self.touch_media_low = True
            #self.log("Toco  media low en price {} con delta de {}".format(actual_price, self.RMSE_low),  to_ui = True, date = self.datetime[0])

    def is_touch_media_high(self, actual_price):
        #low_media = self.ensambleIndicators.mediaEstimadorLow_iterada3
        low_media = self.ensambleIndicators.mediaEstimadorHigh
        if actual_price <= low_media + self.RMSE_low_acrecentada and actual_price >= low_media - self.RMSE_low_acrecentada:
            self.touch_media_high= True

    def is_touch_low_media_iterada_3(self, actual_price, filter_price):
        low_media_3 = self.ensambleIndicators.mediaEstimadorLow_iterada3
        if actual_price >= (low_media_3 - self.RMSE_low) and actual_price <= low_media_3 + self.RMSE_low:
            if self.touch_media_low_iterada_3 == False:
                self.first_touch_filter = filter_price
            self.touch_media_low_iterada_3 = True
            self.log("Toco  media low itereada 3  en price {} ".format(actual_price),  to_ui = True, date = self.datetime[0])
        #else:
        #    self.touch_media_low_iterada_3 = False
    
    def is_touch_high_media_iterada_3_acrecentada(self, actual_price, filter_price):
        #low_media_3 = self.ensambleIndicators.mediaEstimadorLow_iterada3
        low_media_3 = self.ensambleIndicators.mediaEstimadorHigh
        if actual_price >= (low_media_3 - self.RMSE_low_acrecentada) and actual_price <= low_media_3 + self.RMSE_low_acrecentada:
            if self.touch_media_high_iterada_3 == False:
                self.first_touch_filter_acrecentada = filter_price
            self.touch_media_high_iterada_3 = True
    
    def is_delta_aceleration(self, actual_price):
        if actual_price - self.first_touch_filter >= self.delta_aceleration_low:
            self.delta_aceleration =  True
            #self.log("Tuvo una aceleracion despues de media iterada en  {} con delta de {}".format(actual_price, self.delta_aceleration_low),  to_ui = True, date = self.datetime[0])
        else :
            self.delta_aceleration = False
    
    def is_delta_aceleration_acrecentada(self, actual_price):
        #if actual_price - self.first_touch_filter >= self.delta_aceleration_low:
        if actual_price - self.first_touch_filter_acrecentada >= self.delta_aceleration_low_acrecentada:
            self.delta_aceleration_acrecentada =  True
            #self.log("Tuvo una aceleracion despues de media iterada en  {} con delta de {}".format(actual_price, self.delta_aceleration_low),  to_ui = True, date = self.datetime[0])
        else :
            self.delta_aceleration_acrecentada = False
    
    def delta_high_mean_3_succes(self, actual_price):
        high_media_3 = self.ensambleIndicators.mediaEstimadorHigh_iterada3
        if high_media_3 - actual_price > self.min_high_prediction:
            return True
        return False

    def do_long(self, time, price):
        self.jsonParser.addBuyOperation(time, 
                                price, 
                                price, 
                                0, 
                                0)

    def do_short(self, time, price):
        self.trade_made = True
        self.jsonParser.addSellOperation(time, 
                                price, 
                                price, 
                                0, 
                                0)
        self.jsonParser.addTrade(price - self.buy_price, 0)
        profit_ratio = price/self.buy_price
        dummy_acum_capital = self.acum_capital * profit_ratio
        
        #self.set_acum_capital(dummy_acum_capital)

        self.acum_capital_low_high = self.acum_capital_low_high * profit_ratio
        message = "Profit: " + str(profit_ratio - 1) + " Acum Capital: " + str(self.acum_capital)
        self.log(message,  to_ui = True, date = self.datetime[0])
        message = "Profit: " + str(profit_ratio - 1) + " Acum Capital Low High: " + str(self.acum_capital_low_high)
        self.log(message,  to_ui = True, date = self.datetime[0])
        if self.acum_capital >= self.max_profit:
            self.log("Max objetive general reached!",  to_ui = True, date = self.datetime[0])
            #self.continue_acrecentada_strategy = False
            #self.continue_low_to_high_strategy = False
        if self.acum_capital <= self.min_profit:
            self.log("Min objetive general reached. Stop for today",  to_ui = True, date = self.datetime[0])
            #self.continue_acrecentada_strategy = False
            #self.continue_low_to_high_strategy = False
    
    def do_short_acrecentada(self, time, price):
        self.trade_made = True
        self.jsonParser.addSellOperation(time, 
                                price, 
                                price, 
                                0, 
                                0)
        self.jsonParser.addTrade(price - self.buy_price_acrecentada, 0)
        profit_ratio = price/self.buy_price_acrecentada
        self.acum_capital_acrecentada = self.acum_capital_acrecentada * profit_ratio
        dummy_acum_capital = self.acum_capital * profit_ratio
        #self.set_acum_capital(dummy_acum_capital)
        message = "Profit: " + str(profit_ratio - 1) + " Acum Capital : " + str(self.acum_capital)
        self.log(message,  to_ui = True, date = self.datetime[0])
        message = "Profit: " + str(profit_ratio - 1) + " Acum Capital acrecentada: " + str(self.acum_capital_acrecentada)
        self.log(message,  to_ui = True, date = self.datetime[0])
        if self.acum_capital >= self.max_profit:
            self.log("Max objetive general reached!",  to_ui = True, date = self.datetime[0])
            #self.continue_acrecentada_strategy = False
            #self.continue_low_to_high_strategy = False
        if self.acum_capital <= self.min_profit:
            self.log("Min objetive general reached. Stop for today",  to_ui = True, date = self.datetime[0])
            #self.continue_acrecentada_strategy = False
            #self.continue_low_to_high_strategy = False

    def do_binance_trade(self, buy_price, sell_price):
        profit_ratio = sell_price / buy_price
        self.acum_capital_binance = self.acum_capital_binance * profit_ratio * (1 - 0.001) * (1 - 0.001) 
        self.actualize_long_short_strategy_profit(buy_price, sell_price)

    # sobreescrive retorno de wallet balance
    def get_wallet_balance(self):
        message = "El capital total es " + str(self.acum_capital)
        message = message + "\n El capital de acrecentada es " + str(self.acum_capital_acrecentada)
        message = message + "\n El capital de low - high es  " + str(self.acum_capital_low_high)
        return message

    def clean_hour_objective(self):
        self.count_mins =  self.count_mins + 1
        if self.count_mins == (60/self.candle_min):
            self.count_mins = 0
            message = "Paso una hora, se restablecen objetivos"
            #self.log(message,  to_ui = True, date = self.datetime[0])
            self.set_limit_profit_objectives()
            profit = self.acum_capital / self.acum_capital_previous 
            message = "Profit de la hora " + str(profit)
            #self.log(message,  to_ui = True, date = self.datetime[0])
            self.acum_capital_previous = self.acum_capital 
            self.profit_history.append(profit)

    def get_buy_operation_info(self):
        return {
            "is_order": self.is_order,
            "buy_price_binance": self.buy_price_binance,
            "buy_price": self.buy_price,
            "buy_price_actual": self.buy_price_actual,
            "last_actual_price": self.actual_price
        }

    def set_buy_operation(self,buy_operation_info):
        self.do_binance_trade(buy_operation_info["buy_price_binance"],buy_operation_info["last_actual_price"] )
        profit_ratio = buy_operation_info["last_actual_price"] / buy_operation_info["buy_price_binance"]
        message = "Sell cierre 12 hs Profit: " + str(profit_ratio - 1) + " Acum Capital x5: " + str(self.acum_capital_leverage5)
        self.log(message,  to_ui = True, date = "none")
        #self.buy_price_binance = buy_operation_info["buy_price_binance"]
        #self.buy_price = buy_operation_info["buy_price"]
        #self.buy_price_actual = buy_operation_info["buy_price_actual"]
        #self.is_order = True
        #self.trade_made = False
        #self.pre_sell = False
    
    # https://mathcracker.com/es/generador-grafico-funcion-exponencial#results
    # tasa de cambio 0.02, funcion valor inicial 1, 1e ^0.02t
    def dynamic_cota_high(self,t): 
        total_tiempos = 12*(60/self.candle_min) # en 12 horas,el peor de los casos t es incremental entre 1 y 48 en peor de los casos
        indice = math.e**(0.02*(total_tiempos - t)) / math.e**(0.02*total_tiempos) # normaliza entre 0 y 1
        min = 0.004
        max = self.max_profit_strategy
        delta = max - min
        return min + delta*indice

    def next(self):
        # if self.status != "LIVE" and ENV == PRODUCTION:  # waiting for live status in production
        #     return

        if self.order:  # waiting for pending order
            return

        close  = self.datas[0].close[0]
        actual_price = close

        if MULTIPLE_INSTANCE == True:
            self.actual_price = close
        
        if ENV == PRODUCTION:
            actual_price_phemex = self.datas[2].close[0]
        else:
            actual_price_phemex = 0.01 

        #self.log('Close: %.3f %% '  % close)
        self.jsonParser.addTick(self.datetime[0], actual_price)
        self.jsonParser.addTickPhemex(self.datetime[0], actual_price_phemex)
        
        if MULTIPLE_INSTANCE == False:
            self.log('Close: %.3f %% '  % float(close))
            self.log('Close Phemex: %.3f %% '  % float(actual_price_phemex))

        self.mean_filter_ticks.append({"value":actual_price,"date":self.datetime[0]})
        if  len(self.mean_filter_ticks) == self.mean_filter_lag:
            self.filter_ready =  True 
            filter_price = self.create_filter_mean(self.mean_filter_ticks, self.datetime[0])
            self.jsonParser.add_average_tick(self.datetime[0], filter_price["value"])
            # clean for memory 
            self.mean_filter_ticks.pop(0)
        
        #########################################
        #           fast trading low high       #
        #########################################

        if(self.indicators_ready and self.filter_ready and self.pre_buy_acrecentada == False and self.continue_low_to_high_strategy == True):
            self.total_ticks = self.total_ticks + 1 
            if self.total_ticks <= self.max_ticks and self.is_order == False:
                # No le importa si toco high #
                # self.is_touch_high_media_iterada_3(actual_price)
                # se fija si toco "algun estimador high low media iterada 3"
                self.is_touch_high_media_iterada_3(actual_price)
                if self.touch_high_media_iterada_3 == False:
                    if self.touch_media_low_iterada_3 == False:
                        # Se activa cuando toca touch media iterada 3
                        self.is_touch_low_media_iterada_3(actual_price, filter_price["value"])
                    else:
                        if self.delta_aceleration == False:
                            # tiene que superar un delta de aceleracion    
                            self.is_delta_aceleration(filter_price["value"])
                        else:                       
                            if self.pre_buy == False and self.trade_made == False and self.delta_high_mean_3_succes(actual_price) == True:
                                message = "Phemex pre-buy: " + str(actual_price_phemex) + " Delta Binance: " + str(actual_price - actual_price_phemex)
                                self.log(message,  to_ui = True, date = self.datetime[0])
                                self.pre_buy_price = actual_price_phemex
                                self.buy_price_binance = actual_price
                                self.pre_buy = True
                                self.tick_buy_time = 0 
                                if ENV == PRODUCTION and TESTING_PRODUCTION == False and LIVE == True:
                                    self.phemex_automation.buy()
            
            if self.pre_buy == True and self.trade_made == False and self.is_order == False:
                if self.pre_buy_price != actual_price_phemex or ENV == DEVELOPMENT:
                    self.do_long(self.datetime[0], actual_price_phemex)
                    self.buy_price = actual_price_phemex
                    self.buy_price_actual = actual_price
                    # limite hasta donde puede aguantar antes de vender
                    self.low_media_profit_limit = ((self.ensambleIndicators.mediaEstimadorLow - self.RMSE_low ) / self.buy_price_actual ) - 1
                    self.is_order = True
                    self.buy_tick = self.total_ticks
                    message = "Phemex buy: " + str(actual_price_phemex) + " Delta action phemex: " + str(actual_price_phemex - self.pre_buy_price)
                    self.log(message,  to_ui = True, date = self.datetime[0], send_telegram=True)
                    self.jsonParser.set_subida_estrepitosa(1, self.total_ticks)

            if self.is_order == True and self.trade_made == False and self.pre_sell == False:
                if  ENV == PRODUCTION:
                    profit = (actual_price / self.buy_price ) - 1
                else:
                    profit = (actual_price / self.buy_price_actual ) - 1
                
                
                profit_filter = (filter_price["value"] / self.buy_price_actual ) - 1
                profit_phemex = (actual_price_phemex / self.buy_price ) - 1
                do_sell = False
                dynamic_profit = self.dynamic_cota_high(self.tick_buy_time) # no cambio mucho... se puede precindir
                # print("dynamic profit high es " + str(dynamic_profit) + " t=" + str(self.tick_buy_time))
                #if profit_filter <= self.low_media_profit_limit:
                #    do_sell = True
                if profit >= 0.03:
                    do_sell = True
                if profit <= -0.015:
                    do_sell = True
                #if self.total_ticks >= (self.mean_tick - 10):
                #    do_sell = True

                if do_sell == True:
                    self.do_binance_trade(self.buy_price_binance, actual_price) 
                    self.pre_sell = True
                    self.pre_sell_price = actual_price_phemex
                    message = "Phemex pre sell: " + str(actual_price_phemex) + " Delta Binance: " + str(actual_price - actual_price_phemex)
                    self.log(message,  to_ui = True, date = self.datetime[0])
                    if ENV == PRODUCTION and TESTING_PRODUCTION == False and LIVE == True:
                        self.phemex_automation.sell()
                
            if self.is_order == True and self.pre_sell == True and self.trade_made == False and (self.pre_sell_price != actual_price_phemex or ENV == DEVELOPMENT):
                self.do_short(self.datetime[0], actual_price_phemex)
                message = "Phemex sell: " + str(actual_price_phemex) + " Delta action phemex: " + str(actual_price - self.pre_sell_price)
                self.log(message,  to_ui = True, date = self.datetime[0])
                do_sell = False
                self.pre_sell = False
                self.is_order = False
        

        
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
                if MULTIPLE_INSTANCE == False:
                    print("New Indicators Ready!")
                self.refresh()
                self.clean_hour_objective()
                self.tick_buy_time = self.tick_buy_time + 1 
                    
