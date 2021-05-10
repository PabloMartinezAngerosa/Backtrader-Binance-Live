# #!/usr/bin/env python3

import backtrader as bt

from config import ENV, PRODUCTION
from strategies.base import StrategyBase

from config import ENV, PRODUCTION, STRATEGY, TESTING_PRODUCTION, LIVE, UPDATE_PARAMS_FUERZA_BRUTA
import numpy as np
import pandas as pd

class FastTradingNoFeeLowHigh(StrategyBase):

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

        self.RMSE_low = 40
        self.RMSE_high = 30
        self.delta_aceleration_low = 12
        

        self.mean_tick = STRATEGY.get("mean_tick_dev")
        if ENV == PRODUCTION:
            self.mean_tick = STRATEGY.get("mean_tick_prod")

        self.max_ticks = self.mean_tick * 0.8
        self.active_no_loss_profit = False


        #self.dataclose = self.datas[0].close
        self.mean_filter_ticks = []
        self.mean_filter_lag = 7
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
        self.touch_media_low = False
        self.touch_high_media_iterada_3 = False
        self.touch_media_low_iterada_3 = False
        self.delta_aceleration = False
        self.is_order = False
        self.buy_price = 0
        self.buy_price_actual = 0
        self.filter_ready = False 
        self.active_no_loss_profit = False
        self.trade_made = False
    
    def is_touch_high_media_iterada_3(self, actual_price):
        high_media_3 = self.ensambleIndicators.mediaEstimadorHigh_iterada3
        if actual_price >= high_media_3 - self.RMSE_high:
            self.touch_high_media_iterada_3 = True
            #self.log("Toco high media iterada 3 en price {} con delta de {}".format(actual_price, self.RMSE_high),  to_ui = True, date = self.datetime[0])

    def is_touch_media_low(self, actual_price):
        low_media = self.ensambleIndicators.mediaEstimadorLow
        if actual_price <= low_media + self.RMSE_low and actual_price >= low_media - self.RMSE_low:
            self.touch_media_low = True
            #self.log("Toco  media low en price {} con delta de {}".format(actual_price, self.RMSE_low),  to_ui = True, date = self.datetime[0])

    def is_touch_low_media_iterada_3(self, actual_price):
        low_media_3 = self.ensambleIndicators.mediaEstimadorLow_iterada3
        if actual_price >= low_media_3:
            self.touch_media_low_iterada_3 = True
            #self.log("Toco  media low itereada 3  en price {} ".format(actual_price),  to_ui = True, date = self.datetime[0])
        else:
            self.touch_media_low_iterada_3 = False
    
    def is_delta_aceleration(self, actual_price):
        low_media_3 = self.ensambleIndicators.mediaEstimadorLow_iterada3
        if actual_price - low_media_3 >= self.delta_aceleration_low:
            self.delta_aceleration =  True
            #self.log("Tuvo una aceleracion despues de media iterada en  {} con delta de {}".format(actual_price, self.delta_aceleration_low),  to_ui = True, date = self.datetime[0])
        else :
            self.delta_aceleration = False
    
    def do_long(self, time, price):
        if ENV == PRODUCTION and TESTING_PRODUCTION == False and LIVE == True:
            self.phemex_automation.buy()
        self.jsonParser.addBuyOperation(time, 
                                price, 
                                price, 
                                0, 
                                0)

    def do_short(self, time, price):
        if ENV == PRODUCTION and TESTING_PRODUCTION == False and LIVE == True:
            self.phemex_automation.sell()
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
        

        self.log('Close: %.3f %% '  % float(self.data0.close[-1]))

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
                self.is_touch_high_media_iterada_3(actual_price)
                # se fija si toco "algun estimador high low media iterada 3"
                if self.touch_high_media_iterada_3 == False:
                    self.is_touch_media_low(actual_price)
                    if self.touch_media_low == True:
                        self.is_touch_low_media_iterada_3(actual_price)
                        if self.touch_media_low_iterada_3 == True:
                            self.is_delta_aceleration(filter_price["value"])
                            if self.delta_aceleration == True:
                                if self.is_order == False and self.trade_made == False:
                                    self.do_long(self.datetime[0], actual_price_phemex)
                                    message = "Phemex buy: " + str(actual_price_phemex) + " Delta Binance: " + str(actual_price - actual_price_phemex)
                                    self.log(message,  to_ui = True, date = self.datetime[0])
                                    self.buy_price = actual_price_phemex
                                    self.buy_price_actual = actual_price
                                    self.is_order = True
                                    self.buy_tick = self.total_ticks
                                    self.jsonParser.set_subida_estrepitosa(1, self.total_ticks)

            if self.is_order == True and self.trade_made == False:
                profit = (actual_price / self.buy_price_actual ) - 1
                profit_phemex = (actual_price_phemex / self.buy_price ) - 1
                do_sell = False
                if profit >= 0.0005:
                    self.active_no_loss_profit = True
                if profit <= 0.0001 and  self.active_no_loss_profit == True:
                    do_sell = True
                    self.do_short(self.datetime[0], actual_price_phemex)
                if profit <= -0.0005:
                    do_sell = True
                    self.do_short(self.datetime[0], actual_price_phemex)
                if profit_phemex >= 0.0008:
                    do_sell = True
                    self.do_short(self.datetime[0], actual_price_phemex)
                if self.total_ticks >= (self.mean_tick - 2):
                    do_sell = True
                    self.do_short(self.datetime[0], actual_price_phemex)
                if do_sell == True:
                    message = "Phemex sell: " + str(actual_price_phemex) + " Delta Binance: " + str(actual_price - actual_price_phemex)
                    self.log(message,  to_ui = True, date = self.datetime[0])
                    do_sell = False

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
                #print("New Indicators Ready!")
                self.refresh()

