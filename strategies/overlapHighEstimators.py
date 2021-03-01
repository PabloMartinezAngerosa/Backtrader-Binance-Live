# #!/usr/bin/env python3

import backtrader as bt

from config import ENV, PRODUCTION, STRATEGY
from utils import send_telegram_message
from strategies.base import StrategyBase


class OverlapHighEstimators(StrategyBase):

    # Moving average parameters
    # params = (('pfast',20),('pslow',50),)

    def __init__(self):
        StrategyBase.__init__(self)

        # configuration
        self.ensambleIndicatorsLags = STRATEGY.get("lags")
        self.ensambleIndicatorsLengthFrames = STRATEGY.get("length_frames")
        self.candle_min = STRATEGY.get("candle_min")

        self.log("Using Over lap High Estimators strategy")
        self.lendata1 = 0
        self.lagsReady = False
        self.actual_tick = 0
        self.mean_tick = STRATEGY.get("mean_tick_dev")
        if ENV == PRODUCTION:
            self.mean_tick = STRATEGY.get("mean_tick_prod")
            
        self.order = None
        self.name = "OverlapHighEstimators"

        self.indicators_ready = False

        self.tickMax = 0.70 # 75% de los ticks de la vela deja ejecutar
        self.highDeltaSup = 25 # cuanto se agrega al tercer estimador mas alto para asegurar suba y ejecutar compra
        self.delta_tick = 20 # cantidad de ticks permitidos para certificar suba acelerada
        self.stop_loss = 50 # cuanto se deja bajar desde la compra
        self.min_gain = 160 # ganancia minima empieza dinamico
        self.delta_stop_loss_high = 30 # cuanto deja bajar en el high dinamico

        self.high1 = {"value":0, "touch": False, "tick":0}
        self.high2 = {"value":0, "touch": False, "tick":0}
        self.high3 = {"value":0, "touch": False, "tick":0}
        self.high_cota_sup = {"value":0, "touch": False, "tick":0}
        self.buy_price = 0
        self.min_gain_dynamic = self.min_gain
        self.made_trade = False

        self.orderActive  = False

        self.jsonParser.add_strategy_name(self.name)

    def refreshOverlapHighEstimatorsValues(self):
        self.high1["value"] = self.ensambleIndicators.indicatorsHigh[3]
        self.high2["value"] = self.ensambleIndicators.indicatorsHigh[2]
        self.high3["value"] = self.ensambleIndicators.indicatorsHigh[1]
        self.high_cota_sup["value"] = self.ensambleIndicators.indicatorsHigh[1] + self.highDeltaSup
        self.min_gain_dynamic = self.min_gain
        self.made_trade = False

    def update_overlap(self, high_ref, price, tick):
        if price >= high_ref["value"]:
            if high_ref["touch"] == False:
                high_ref["touch"] = True
                high_ref["tick"] = tick
        else:
            high_ref["touch"] = False
            high_ref["tick"] = 0

    def check_high_estimations(self):
        '''
            cuando existe un error en el calculo de los estimadores el valor es 0
        '''
        for price in self.ensambleIndicators.indicatorsHigh:
            if price == 0:
                return False
        return True

    def check_high_estimator_overlap(self, price, tick):

        self.update_overlap(self.high1, price, tick)
        self.update_overlap(self.high2, price, tick)
        self.update_overlap(self.high3, price, tick)
        self.update_overlap(self.high_cota_sup, price, tick)

        if self.high_cota_sup["touch"] == True:
            delta_tick = self.high_cota_sup["tick"] - self.high1["tick"]
            if delta_tick > 0 and delta_tick <= self.delta_tick:
                return True
        
        return False

    def check_sell_operation(self, price, tick):

        # stop loss
        if self.buy_price - price >= self.stop_loss:
            return True

        # fixed high to dynamic
        '''
        delta_price = price - self.buy_price
        if delta_price > self.min_gain_dynamic:
            self.min_gain_dynamic = delta_price
        else:
            if self.min_gain_dynamic - delta_price > self.delta_stop_loss_high:
                return True
        '''

        return False




    def next(self):
        # if self.status != "LIVE" and ENV == PRODUCTION:  # waiting for live status in production
        #     return
        actual_price  = self.datas[0].close[0]
        self.actual_tick = self.actual_tick + 1
        self.jsonParser.addTick(self.datetime[0], actual_price)
        
        if self.order:  # waiting for pending order
            return

        self.log('Actual Price: %.3f %% '  % actual_price)
        
        # si estan listos los indicadores comienza la estrategia
        if self.indicators_ready == True and self.made_trade == False:
            if self.last_operation != "BUY" and  self.actual_tick < (self.mean_tick * self.tickMax):
                if self.check_high_estimator_overlap(actual_price, self.actual_tick) == True:
                    print("tres seguidos mas el delta, esto es suba! compra!")
                    self.buy_price = actual_price
                    self.long()
            
            if self.last_operation != "SELL":
                if self.check_sell_operation(actual_price, self.actual_tick) == True:
                    self.short()
                    self.made_trade = True
                # va al close, pro ticks antes para q permanezca en
                # la misma vela con el lag posible de la ejecucion d orden.
                if self.actual_tick >= (self.mean_tick - 10):
                    print("esta llegando close y no toco high. ejecuta compra")
                    self.short()
                    self.made_trade = True


        
        if len(self.data1.low) > self.lendata1:
            # si la lutima operacion es comprar y no realizo transaccion compra y venta
               # vende 
            self.lendata1 += 1
            self.actual_tick = 0

            print("Cada cambio de Vela de " + str(self.candle_min)  + " min")
            print(self.data1.low[0])
            
            #low  = self.datas[1].low[0]
            #high = self.datas[1].high[0]

            #self.log('Low : %.3f %% '  % low)
            #self.log('High 1 min tick : %.3f %% '  % high)
            #self.log('Low data1: %.3f %% '  % float(self.data1.low[0]))
            #self.log('Low -1 data1: %.3f %% '  % float(self.data1.low[-1]))

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
                self.indicators_ready = self.check_high_estimations()
                self.refreshOverlapHighEstimatorsValues()
        


