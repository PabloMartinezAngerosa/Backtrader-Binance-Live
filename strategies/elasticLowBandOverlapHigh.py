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

        self.stoploss = 100
        self.cota_superior_low = 30
        self.elastic_margin_low = 20

        self.elastic_margin_high = 30
        self.stoploss_elastic_high = 100
        self.min_elastic_high_low = 180


        self.actual_tick = 0
        self.mean_tick = STRATEGY.get("mean_tick_dev")
        if ENV == PRODUCTION:
            self.mean_tick = STRATEGY.get("mean_tick_prod")

        self.indicators_ready = False
        self.orderActive  = False
        self.made_trade = False
        self.low_active =  False
        self.high_active = False
        self.filter_price_is_inflection = False
        self.filter_price_candle = []

        self.is_first_tick = True
        self.is_active_elastic_high = False
        self.low_upper = 0
        self.high_upper = 0

        self.jsonParser.add_strategy_name(self.name)

        self.mean_filter_ticks = []
        self.mean_filter_lag = 15
        self.active_elastic_high = 0
    
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
        self.filter_price_is_inflection = False
        self.is_active_elastic_high = False
        self.active_elastic_high = 0
        # volver este a 0 por vela implicar esperar al menos 1 tick para poder hacer los calculos
        # y considerarlo en la estrategia.
        self.filter_price_candle = []
    
    def sell_order(self):
        self.short()
        self.orderActive = False
        self.made_trade = True

    def create_filter_mean(self, filter_tikcs, date):
        sum = 0
        for tick in filter_tikcs:
            sum = sum + tick["value"]
        mean = sum / self.mean_filter_lag
        return {"value":mean,"date":date}

    def average_inflection_point(self, x_1, y_1, x_2, y_2):
        pendiente = (y_2 - y_1) / (x_2 - x_1)
        if  pendiente < 0.0001 and pendiente > -0.0001:
            self.filter_price_is_inflection = True
            self.jsonParser.add_inflection_point(x_2, y_2)
        else:
            self.filter_price_is_inflection = False
    
    def do_long(self, message):
        if self.last_operation != "Buy":
            self.log(message,  to_ui = True, date = self.datetime[0])
            self.long()
            self.orderActive = True
            return True
        return False
        
    def do_short(self, message):
        if self.last_operation != "SELL":
            self.log(message,  to_ui = True, date = self.datetime[0])
            self.sell_order()

    def next(self):
        # if self.status != "LIVE" and ENV == PRODUCTION:  # waiting for live status in production
        #     return
        actual_price  = self.datas[0].close[0]
        self.actual_tick = self.actual_tick + 1
        self.jsonParser.addTick(self.datetime[0], actual_price)

        self.mean_filter_ticks.append({"value":actual_price,"date":self.datetime[0]})
        if  len(self.mean_filter_ticks) == self.mean_filter_lag:
            filter_price = self.create_filter_mean(self.mean_filter_ticks, self.datetime[0])
            self.filter_price_candle.append(filter_price)
            self.jsonParser.add_average_tick(self.datetime[0], filter_price["value"])
            # clean for memory 
            self.mean_filter_ticks.pop(0)
        

        # puntos de inflexion average
        if len(self.filter_price_candle) >=2:
            y_2 = self.filter_price_candle[len(self.filter_price_candle) -1]["value"]
            x_2 = self.filter_price_candle[len(self.filter_price_candle) -1]["date"]
            y_1 = self.filter_price_candle[len(self.filter_price_candle) -2]["value"]
            x_1 = self.filter_price_candle[len(self.filter_price_candle) -2]["date"]
            self.average_inflection_point(x_1, y_1, x_2, y_2)

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

                if self.actual_tick <= (self.mean_tick * 0.6):
                    # elsastic band low
                    if actual_price < self.low_upper + self.cota_superior_low:
                        self.low_active =  True
                    elif actual_price > (self.low_upper + self.cota_superior_low + self.elastic_margin_low) and self.low_active == True:
                        message = "Estuvo en la franja de minimos y ahora marca tendencia alcista, compra!"
                        self.do_long(message)
                    elif actual_price >= self.high_upper and self.high_active == False:
                        self.high_active = True
                    '''
                    elif actual_price >= (self.high_upper + self.elastic_margin_high) and self.high_active == True:
                        message = "Parece una subida estrepitosa paso todos los High! Compra"
                        self.do_long(message)
                    '''
            # busca venta
            else:
                if self.filter_price_is_inflection == True:
                    if filter_price["value"] > self.active_elastic_high: 
                        self.active_elastic_high = filter_price["value"]
                    if self.is_active_elastic_high == False:
                        self.is_active_elastic_high = True
                        if actual_price - self.buy_price_close > 100:
                            message = "El primer punto de inflexion es mayoer que 100,   Vende!."
                            self.do_short(message)

                       
                # stop loss filter average este es en caso que desde la compra no actualiza y va a perdida
                if self.last_operation != "SELL":
                    if self.buy_price_close - filter_price["value"] >= self.stoploss:
                        message = "Llego a un stop loss de $" + str(self.buy_price_close - filter_price["value"]) + ". Vende con perdida."
                        self.do_short(message)
                
                if self.last_operation != "SELL":
                    # elastic high stop loss filtered una vez que toca al menos un active_elastic_high
                    if self.is_active_elastic_high == True:
                        if actual_price - self.buy_price_close > self.min_elastic_high_low:
                            message = "Ya toco inflexion y es mayor que " + str(self.min_elastic_high_low) +",   Vende!."
                            self.do_short(message)

                        elif self.active_elastic_high - filter_price["value"] >= self.stoploss_elastic_high:
                            message = "Llego a un elastic high con stop loss average de $" + str(self.active_elastic_high - filter_price["value"])
                            message = message +  ". Vende con delta de ganancia de " 
                            self.do_short(message)

                
                if self.actual_tick >= (self.mean_tick - 10):
                    message = "esta llegando close y no toco high. ejecuta venta"
                    self.do_short(message)
        
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


