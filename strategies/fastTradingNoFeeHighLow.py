# #!/usr/bin/env python3
'''

Esta estrategia esta basada en estimar low, y vender en high fijo.
Funcionaba bien hasta la bajada que comenzo a funcionar mejor la subida acrecentada.
Esta pensanda para entorno sin Fee y con Phemex.
Dado los desniveles entre Phemex y Binance, funcio bien en velas mas grande de 15/30 minutos.
En medida que se agrandan las velas, el desfasaje se nota menos por la media de la volatiliad en la vela 
la cual aumenta. 

'''
import backtrader as bt

from config import ENV, PRODUCTION
from strategies.base import StrategyBase

from config import ENV, PRODUCTION, STRATEGY, TESTING_PRODUCTION, LIVE, UPDATE_PARAMS_FUERZA_BRUTA
import numpy as np
import pandas as pd

class FastTradingNoFeeHighLow(StrategyBase):

    # Moving average parameters
    # params = (('pfast',20),('pslow',50),)

    def __init__(self, phemex_automation):
        StrategyBase.__init__(self)

        self.log("Using FastTradingNoFeeLowHigh strategy")
        self.lendata1 = 0
        self.indicators_ready = False

        self.ensambleIndicatorsLags = STRATEGY.get("lags")
        self.ensambleIndicatorsLengthFrames = STRATEGY.get("length_frames")
        self.candle_min = STRATEGY.get("candle_min")
        
        self.acum_capital = 100 
        self.acum_capital_binance = 100

        self.RMSE_low = 30
        self.RMSE_high = 120
        self.delta_aceleration_low = 3
        

        self.mean_tick = STRATEGY.get("mean_tick_dev")
        if ENV == PRODUCTION:
            self.mean_tick = STRATEGY.get("mean_tick_prod")

        self.max_ticks = self.mean_tick * 0.8
        self.active_no_loss_profit = False


        #self.dataclose = self.datas[0].close
        self.mean_filter_ticks = []
        self.mean_filter_lag = 5
        self.order = None
        self.trade_made = False
        self.name = "FastTradingNoFeeLowHigh"
        self.refresh()
        self.phemex_automation = phemex_automation

    def create_filter_mean(self, filter_tikcs, date):
        sum = 0
        for tick in filter_tikcs:
            sum = sum + tick["value"]
        mean = sum / self.mean_filter_lag
        return {"value":mean,"date":date}

    def refresh(self):
        self.total_ticks = 0
        self.touch_media_high = False
        self.touch_low_media_iterada_3 = False
        self.touch_media_high_iterada_3 = False
        self.delta_aceleration = False
        self.is_order = False
        self.buy_price = 0
        self.buy_price_actual = 0
        self.filter_ready = False 
        self.active_no_loss_profit = False
        self.trade_made = False
        self.first_touch_filter = 0
        self.pre_buy = False
        self.pre_buy_price = 0
        self.pre_sell = False
        self.pre_sell_price = 0
    
    def is_touch_low_media_iterada_3(self, actual_price):
        low_media_3 = self.ensambleIndicators.mediaEstimadorLow_iterada3
        if actual_price <= low_media_3 + self.RMSE_low:
            self.touch_low_media_iterada_3 = True
            #self.log("Toco high media iterada 3 en price {} con delta de {}".format(actual_price, self.RMSE_high),  to_ui = True, date = self.datetime[0])

    def is_touch_media_high(self, actual_price):
        high_media = self.ensambleIndicators.mediaEstimadorHigh_iterada3
        if actual_price <= high_media + self.RMSE_high and actual_price >= high_media - self.RMSE_high:
            self.touch_media_high = True
            #self.log("Toco  media low en price {} con delta de {}".format(actual_price, self.RMSE_low),  to_ui = True, date = self.datetime[0])

    def is_touch_high_media_iterada_3(self, actual_price, filter_price):
        high_media_3 = self.ensambleIndicators.mediaEstimadorHigh_iterada3
        if actual_price >= (high_media_3 - self.RMSE_high) and actual_price <= high_media_3 + self.RMSE_high:
            if self.touch_media_high_iterada_3 == False:
                self.first_touch_filter = filter_price
            self.touch_media_high_iterada_3 = True
            #self.log("Toco  media low itereada 3  en price {} ".format(actual_price),  to_ui = True, date = self.datetime[0])
        else:
            self.touch_media_high_iterada_3 = False
    
    def is_delta_aceleration(self, actual_price):
        if self.first_touch_filter - actual_price >= self.delta_aceleration_low:
            self.delta_aceleration =  True
            #self.log("Tuvo una aceleracion despues de media iterada en  {} con delta de {}".format(actual_price, self.delta_aceleration_low),  to_ui = True, date = self.datetime[0])
        else :
            self.delta_aceleration = False
    
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
        self.acum_capital = self.acum_capital * profit_ratio
        message = "Profit: " + str(profit_ratio - 1) + " Acum Capital: " + str(self.acum_capital)
        self.log(message,  to_ui = True, date = self.datetime[0])

    def do_binance_trade(self, buy_price, sell_price):
        profit_ratio = sell_price / buy_price
        self.acum_capital_binance = self.acum_capital_binance * profit_ratio * (1 - 0.001) * (1 - 0.001) 
    def next(self):
        # if self.status != "LIVE" and ENV == PRODUCTION:  # waiting for live status in production
        #     return

        if self.order:  # waiting for pending order
            return

        close  = self.datas[0].close[0]
        actual_price = close

        actual_price_phemex = self.datas[2].close[0]

        #self.log('Close: %.3f %% '  % close)
        self.jsonParser.addTick(self.datetime[0], actual_price)
        self.jsonParser.addTickPhemex(self.datetime[0], actual_price_phemex)
        

        self.log('Close: %.3f %% '  % float(close))
        self.log('Close Phemex: %.3f %% '  % float(actual_price_phemex))

        self.mean_filter_ticks.append({"value":actual_price,"date":self.datetime[0]})
        if  len(self.mean_filter_ticks) == self.mean_filter_lag:
            self.filter_ready =  True 
            filter_price = self.create_filter_mean(self.mean_filter_ticks, self.datetime[0])
            self.jsonParser.add_average_tick(self.datetime[0], filter_price["value"])
            # clean for memory 
            self.mean_filter_ticks.pop(0)
        
        #  update stategy indicators 
        # self.updateIndicatorsEnsambleLinearModels(self.data0)
        if(self.indicators_ready and self.filter_ready):
            self.total_ticks = self.total_ticks + 1 
            if self.total_ticks <= self.max_ticks:
                self.is_touch_low_media_iterada_3(actual_price)
                # se fija si toco "algun estimador high low media iterada 3"
                if self.touch_low_media_iterada_3 == False:
                    self.is_touch_media_high(actual_price)
                    if self.touch_media_high == True:
                        self.is_touch_high_media_iterada_3(actual_price, filter_price["value"])
                        if self.touch_media_high_iterada_3 == True:
                            self.is_delta_aceleration(filter_price["value"])
                            if self.delta_aceleration == True:
                                if self.pre_buy == False and self.trade_made == False:
                                    message = "Phemex pre-buy: " + str(actual_price_phemex) + " Delta Binance: " + str(actual_price - actual_price_phemex)
                                    self.log(message,  to_ui = True, date = self.datetime[0])
                                    self.pre_buy_price = actual_price_phemex
                                    self.pre_buy = True
                                    if ENV == PRODUCTION and TESTING_PRODUCTION == False and LIVE == True:
                                        self.phemex_automation.buy()
            
            if self.pre_buy == True and self.trade_made == False and self.is_order == False:
                if self.pre_buy_price != actual_price_phemex:
                    self.do_long(self.datetime[0], actual_price_phemex)
                    self.buy_price = actual_price_phemex
                    self.buy_price_actual = actual_price
                    self.is_order = True
                    self.buy_tick = self.total_ticks
                    message = "Phemex buy: " + str(actual_price_phemex) + " Delta action phemex: " + str(actual_price_phemex - self.pre_buy_price)
                    self.log(message,  to_ui = True, date = self.datetime[0])
                    self.jsonParser.set_subida_estrepitosa(1, self.total_ticks)

            if self.is_order == True and self.trade_made == False and self.pre_sell == False:
                profit = 1 - (actual_price / self.buy_price_actual )
                profit_phemex = 1 - (actual_price_phemex / self.buy_price )
                do_sell = False
                if profit >= 0.0035:
                    self.active_no_loss_profit = True
                if profit <= 0.002 and  self.active_no_loss_profit == True:
                    do_sell = True
                if profit <= -0.004:
                    do_sell = True
                if profit >= 0.008:
                    do_sell = True
                if self.total_ticks >= (self.mean_tick - 10):
                    do_sell = True

                if do_sell == True:
                    self.do_binance_trade(self.buy_price_actual, actual_price)
                    self.pre_sell = True
                    self.pre_sell_price = actual_price_phemex
                    message = "Phemex pre sell: " + str(actual_price_phemex) + " Delta Binance: " + str(actual_price - actual_price_phemex)
                    self.log(message,  to_ui = True, date = self.datetime[0])
                    if ENV == PRODUCTION and TESTING_PRODUCTION == False and LIVE == True:
                        self.phemex_automation.sell()
                
            if self.is_order == True and self.pre_sell == True and self.trade_made == False and self.pre_sell_price != actual_price_phemex:
                self.do_short(self.datetime[0], actual_price_phemex)
                message = "Phemex sell: " + str(actual_price_phemex) + " Delta action phemex: " + str(actual_price - self.pre_sell_price)
                self.log(message,  to_ui = True, date = self.datetime[0])
                do_sell = False
                self.pre_sell = False

               # fast, si llega a un delta rapido vende, la idea con 4 seguidos lograr un delta d 300 que singifique subir un escalon 1.4

               # si llega a un stop loss vende
               # si llega a frame 30 vende
        
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
                print("New Indicators Ready!")
                self.refresh()

