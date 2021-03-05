# #!/usr/bin/env python3

import backtrader as bt

from config import ENV, PRODUCTION, STRATEGY
from strategies.base import StrategyBase


class ElasticLowBandOverlapHigh(StrategyBase):

    # Moving average parameters
    # params = (('pfast',20),('pslow',50),)

    def __init__(self):
        StrategyBase.__init__(self)

        # configuration
        self.ensambleIndicatorsLags = STRATEGY.get("lags")
        self.ensambleIndicatorsLengthFrames = STRATEGY.get("length_frames")
        self.candle_min = STRATEGY.get("candle_min")

        self.log("Using Elastic-Low-Band-Overlap-high")
        self.lendata1 = 0
        self.lagsReady = False
        
        self.order = None
        self.name = "ElasticLowBandOverlapHigh"

        self.cota_superior_low = 30
        self.elastic_margin_low = 20

        self.elastic_margin_high = 30

        self.actual_tick = 0
        self.mean_tick = STRATEGY.get("mean_tick_dev")
        if ENV == PRODUCTION:
            self.mean_tick = STRATEGY.get("mean_tick_prod")

        self.indicators_ready = False
        self.orderActive  = False
        self.made_trade = False
        self.low_active =  False
        self.high_active = False

        self.is_first_tick = True
        self.low_upper = 0
        self.high_upper = 0

        self.jsonParser.add_strategy_name(self.name)
    
    def get_high_low(self):
        # los indicadores estan de menor a mayor
        # se busca el valor mas chico
        high_low = 0
        for low_estimation in self.ensambleIndicators.indicatorsLow:
            if low_estimation > high_low and low_estimation < self.open_candle:
                high_low = low_estimation
        return high_low

    def get_high_high(self):
        '''
        Se busca el estimador mas alto. Los estimadores High estan en orden DESC.
        '''
        return self.ensambleIndicators.indicatorsHigh[0]
   
    def refresh_variables(self):
        self.is_first_tick = True
        self.made_trade = False
        self.low_active = False
        self.high_active = False
    
    def sell_order(self):
        self.short()
        self.orderActive = False
        self.made_trade = True

    def next(self):
        # if self.status != "LIVE" and ENV == PRODUCTION:  # waiting for live status in production
        #     return
        actual_price  = self.datas[0].close[0]
        self.actual_tick = self.actual_tick + 1
        self.jsonParser.addTick(self.datetime[0], actual_price)
        
        if self.order:  # waiting for pending order
            return

        self.log('Actual Price: %.3f %% '  % actual_price)
        
        # self.log()
        # self.log("Compra",  to_ui = True, date = self.datetime[0])
        # self.short()

        if(self.indicators_ready and self.made_trade == False):
            if self.is_first_tick == True:
                self.is_first_tick = False
                self.open_candle = actual_price
                self.low_upper = self.get_high_low()
                self.high_upper = self.get_high_high()
                self.log("el low_upper es " + str(self.low_upper) + " - delta open: " + str(self.open_candle - self.low_upper),  to_ui = True, date = self.datetime[0])
                self.log("el high_upper es " + str(self.high_upper)) 
            # Busca compra
            if (self.orderActive == False):
                # elsastic band low
                if actual_price < self.low_upper + self.cota_superior_low:
                    self.low_active =  True
                elif actual_price > (self.low_upper + self.cota_superior_low + self.elastic_margin_low) and self.low_active == True:
                    if self.last_operation != "Buy":
                        self.log("Estuvo en la franja de minimos y ahora marca tendencia alcista, compra!",  to_ui = True, date = self.datetime[0])
                        self.long()
                        self.orderActive = True
                elif actual_price >= self.high_upper and self.high_active == False:
                    self.high_active = True
                elif actual_price >= (self.high_upper + self.elastic_margin_high) and self.high_active == True:
                    if self.last_operation != "Buy":
                        self.log("Parece una subida estrepitosa paso todos los High! Compra",  to_ui = True, date = self.datetime[0])
                        self.long()
                        self.orderActive = True

                # elastic band high (overlapHigh)
                
            else:
                if self.actual_tick >= (self.mean_tick - 10):
                    if self.last_operation != "SELL":
                        self.log("esta llegando close y no toco high. ejecuta venta",  to_ui = True, date = self.datetime[0])
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


