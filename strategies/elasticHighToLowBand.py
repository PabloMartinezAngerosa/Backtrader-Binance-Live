# #!/usr/bin/env python3

import backtrader as bt

from config import ENV, PRODUCTION, STRATEGY, TESTING_PRODUCTION, LIVE, UPDATE_PARAMS_FUERZA_BRUTA
from strategies.base import StrategyBase
from binance.enums import *
import asyncio



class ElasticHighToLowBand(StrategyBase):

    # Moving average parameters
    # params = (('pfast',20),('pslow',50),)

    def __init__(self, stand_alone = False):
        StrategyBase.__init__(self, stand_alone = stand_alone)

        # configuration
        self.STANDALONE = stand_alone

        self.broker = None
        self.elasticLowBandOverlapHighFuerzaBruta = None
        self.ensambleIndicatorsLags = STRATEGY.get("lags")
        self.ensambleIndicatorsLengthFrames = STRATEGY.get("length_frames")
        self.candle_min = STRATEGY.get("candle_min")

        self.log("Using ElasticHighToLowBand")
        self.lendata1 = 0
        self.lagsReady = False
        
        self.order = None
        self.name = "ElasticHighToLowBand"
        
        # parametros se modifican por fuerza bruta #
        self.check_buy_conditions_buy_conditions_value_high = 60
        self.check_buy_conditions_buy_conditions_value_low = 65
        self.fixed_limit_high = 500
        self.check_buy_high = 100
        # se permite tener como referencia low que estan por encima del open en este nivel
        self.cota_superior_open = 160 
        self.stoploss = 85 
        self.cota_superior_lower = 50 
        self.elastic_margin_low = 17.364864864864863
        self.index_high_estimation = 1
        self.minimum_profit_proyected = 206.66666666666666
        self.mean_filter_lag = 7
        self.touch_high_cota = 48.333333333333336
        self.min_gain = 180 # punto en el cual activa high dynamic
        self.min_gain_dynamic = self.min_gain 
        self.low_by_bands = True
        self.max_ticks_to_operate = 0.25 # aggressive operation en inicio
        self.stoploss_lower = 50
        self.cota_superior_low = 28.10810810810811
        self.delta_stop_loss_high = 30 # cuanto permite perder antes de cerra venta en high dinamico
        self.min_gain_without_action = 100 # cuando se vencen los ticks, y no acelero lo esperado corta
        self.max_tick_without_action = 70 # ticks que deja pasar sin accion
        self.min_high_active_tick = 20 # para medir si la aceleracion es suficente
        

        self.elastic_margin_high = 30
        self.stoploss_elastic_high = 100
        self.min_elastic_high_low = 180
        
        self.fixed_limit_high_lower = 120

        
        self.first_inflection_point_min_revenue = 140

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
        self.made_lower_buy = False

        self.is_first_tick = True
        self.is_active_elastic_high = False
        self.low_upper = 0
        self.high_upper = 0

        self.jsonParser.add_strategy_name(self.name)
        self.filter_ready = False
        self.mean_filter_ticks = []
        self.active_elastic_high = 0
        self.touch_high = False
        self.active_lower = False
        self.low_band_active_value = 0
        self.low_band_active = False
        self.check_buy_conditions = False
        self.second_candle = False
        self.previous_candle_last_tick_date = 0
        self.first_time_min_gain = False
        self.buy_tick_time = 0
        
        
    
    def get_high_low(self):
        # los indicadores estan de menor a mayor
        # se busca el valor mas chico
        high_low = 0
        for low_estimation in self.ensambleIndicators.indicatorsLow:
            if low_estimation > high_low and low_estimation < self.open_candle + self.cota_superior_open:
                high_low = low_estimation
        return high_low

    def get_low_low(self):
        # los indicadores estan de menor a mayor
        # se busca el valor mas chico, no toma en cuenta delta low
        high_low = 0
        delta_low = self.ensambleIndicators.deltaMediaOpenLow
        for low_estimation in self.ensambleIndicators.indicatorsLow:
            if low_estimation > high_low and low_estimation < self.open_candle and low_estimation!= delta_low:
                return low_estimation
        return high_low

    def get_high_high(self):
        '''
        Se busca el estimador mas alto. Los estimadores High estan en orden DESC.
        '''
        return self.ensambleIndicators.indicatorsHigh[0]
    
    def check_low_bands(self, actual_price):
        if self.low_band_active == True:
            if actual_price >= self.low_band_active_value:
                return True
        # indicdadores estan de menor a mayor
        # se checka aunque low band active sea true, porque puede bajar de banda
        # y activar nuevas bandas menores
        dummy_index = 0
        for low_estimation in self.ensambleIndicators.indicatorsLow:
            dummy_index = dummy_index + 1
            # en la ultima banda esta la otra configuracion de accion de compra
            if dummy_index < len(self.ensambleIndicators.indicatorsLow):
                if actual_price <= low_estimation and low_estimation < self.open_candle:
                    self.low_band_active = True
                    # el objetivo es cuando toca el high de la siguiente banda para comprar
                    if self.ensambleIndicators.indicatorsLow[dummy_index] < self.low_band_active_value or self.low_band_active_value==0 :
                        self.low_band_active_value = self.ensambleIndicators.indicatorsLow[dummy_index] 
                    break
        return False

   
    def refresh_variables(self):
        self.orderActive = False
        self.made_lower_buy = False
        self.filter_ready = False
        self.is_first_tick = True
        self.made_trade = False
        self.low_active = False
        self.high_active = False
        self.filter_price_is_inflection = False
        self.is_active_elastic_high = False
        self.active_elastic_high = 0
        self.active_lower = False
        # volver este a 0 por vela implicar esperar al menos 1 tick para poder hacer los calculos
        # y considerarlo en la estrategia.
        self.filter_price_candle = []
        self.touch_high = False
        self.low_band_active = False
        self.low_band_active_value = 0
        self.check_buy_conditions = False
        self.min_gain_dynamic = self.min_gain
        self.first_time_min_gain = False
        self.buy_tick_time = 0
    
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

    '''
    def average_inflection_point(self, x_1, y_1, x_2, y_2):
        pendiente = (y_2 - y_1) / (x_2 - x_1)
        if  pendiente < 0.0001 and pendiente > -0.0001:
            self.filter_price_is_inflection = True
            self.jsonParser.add_inflection_point(x_2, y_2)
        else:
            self.filter_price_is_inflection = False
    '''
    
    def do_long(self, message):
        if self.last_operation != "Buy":
            succces_trade = True
            if ENV == PRODUCTION and TESTING_PRODUCTION == False and LIVE == True and self.broker != None and self.STANDALONE == False:
                TRADE_SYMBOL = 'BTCUSDT'
                TRADE_QUANTITY = 0.000419
                succces_trade = self.broker.order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
            if succces_trade == True:
                self.log(message,  to_ui = True, date = self.datetime[0])
                self.long()
                self.orderActive = True
                return True
        return False
        
    def do_short(self, message):
        if self.last_operation != "SELL":
            succces_trade = True
            if ENV == PRODUCTION and TESTING_PRODUCTION == False and LIVE == True and self.broker != None and self.STANDALONE == False:
                TRADE_SYMBOL = 'BTCUSDT'
                TRADE_QUANTITY = 0.000419
                succces_trade = self.broker.order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
            if succces_trade == True:
                self.log(message,  to_ui = True, date = self.datetime[0])
                self.sell_order()
                return True
        return False

    def is_high(self, actual_price):
        # no toma a cuenta al delta estiation
        delta_high = self.ensambleIndicators.deltaMediaOpenHigh
        for high_estimation in self.ensambleIndicators.indicatorsHigh:
            if (high_estimation - self.touch_high_cota) <= actual_price and high_estimation > self.open_candle and high_estimation != delta_high:
                return True
        return False

    def minimum_profit_estimation(self, actual_price, index_high_estimation):
        if index_high_estimation == 1:
            high_estimation = self.ensambleIndicators.mediaEstimadorHigh
        elif index_high_estimation == 2:
            high_estimation = self.ensambleIndicators.mediaEstimadorHigh_iterada2
        elif index_high_estimation == 3:
            high_estimation = self.ensambleIndicators.mediaEstimadorHigh_iterada3
        else:
            high_estimation = self.ensambleIndicators.mediaEstimadorHigh
        if (high_estimation - actual_price) <= self.minimum_profit_proyected and high_estimation > self.open_candle:
                return False
        return True

    def next(self):
        # if self.status != "LIVE" and ENV == PRODUCTION:  # waiting for live status in production
        #     return
        actual_price  = self.datas[0].close[0]
        self.actual_tick = self.actual_tick + 1
        self.jsonParser.addTick(self.datetime[0], actual_price)

        self.mean_filter_ticks.append({"value":actual_price,"date":self.datetime[0]})
        if  len(self.mean_filter_ticks) == self.mean_filter_lag:
            self.filter_ready =  True 
            filter_price = self.create_filter_mean(self.mean_filter_ticks, self.datetime[0])
            self.filter_price_candle.append(filter_price)
            self.jsonParser.add_average_tick(self.datetime[0], filter_price["value"])
            # clean for memory 
            self.mean_filter_ticks.pop(0)
        

        # puntos de inflexion average
        '''
        if len(self.filter_price_candle) >=2:
            y_2 = self.filter_price_candle[len(self.filter_price_candle) -1]["value"]
            x_2 = self.filter_price_candle[len(self.filter_price_candle) -1]["date"]
            y_1 = self.filter_price_candle[len(self.filter_price_candle) -2]["value"]
            x_1 = self.filter_price_candle[len(self.filter_price_candle) -2]["date"]
            self.average_inflection_point(x_1, y_1, x_2, y_2)
        '''

        if self.order:  # waiting for pending order
            return

        self.log('Actual Price: %.3f %% '  % actual_price)
        
        # self.log()
        # self.log("Compra",  to_ui = True, date = self.datetime[0])
        # self.short()
        if(self.indicators_ready and self.made_trade == False and self.filter_ready == True):
            if self.is_first_tick == True:
                self.is_first_tick = False
                self.open_candle = actual_price
                self.low_upper = self.get_high_low()
                self.low_lowwer = self.get_low_low()
                self.high_upper = self.get_high_high()
                self.log("el low_upper es " + str(self.low_upper) + " - delta open: " + str(self.open_candle - self.low_upper),  to_ui = True, date = self.datetime[0])
                self.log("el high_upper es " + str(self.high_upper)) 
            # Busca compra
            if (self.orderActive == False):

                # certifica si no toco high
                if self.touch_high == False:
                    self.touch_high = self.is_high(actual_price)
                    if self.touch_high == True:
                        message = "Toca high antes que Low estimation en $ " + str(actual_price) + ". Ya no realiza trade."
                        self.log(message,  to_ui = True, date = self.datetime[0])

                if self.touch_high == False:
                    # upper low aggresive
                    if self.actual_tick <= (self.mean_tick * self.max_ticks_to_operate):
                        # elsastic band low, utiliza el filtro para asegurar q no son picos. 
                        if filter_price["value"] < self.low_upper + self.cota_superior_low:
                            self.low_active =  True
                        elif filter_price["value"] > (self.low_upper + self.cota_superior_low + self.elastic_margin_low) and self.low_active == True:
                            if self.minimum_profit_estimation(actual_price, self.index_high_estimation) == True:
                                message = "Estuvo en la franja de minimos y ahora marca tendencia alcista, Vende!"
                                #self.check_buy_conditions = True
                                self.orderActive =  True
                                self.buy_price_close = actual_price 
                                self.buy_tick_time = self.actual_tick
                                self.do_long(message)
                            else:
                                message = "Estuvo en la franja de minimos y ahora marca tendencia alcista, pero no alcanza la estimacion minima. No ejecuta trade"
                                self.log(message,  to_ui = True, date = self.datetime[0])
                                # no deja ejecutar mas en trade. es peligroso en general erra.
                                self.touch_high = True
                    
                # overlap high estimation aggresive
                # en este caso no importa si toca high
                '''
                if filter_price["value"] >= self.ensambleIndicators.mediaEstimadorHigh and self.high_active == False and self.actual_tick <= self.min_high_active_tick:
                    self.high_active = True
                    self.high_active_tick = self.actual_tick

                if self.high_active == True:
                    if filter_price["value"] - self.ensambleIndicators.mediaEstimadorHigh >= (self.elastic_margin_low * 2) and self.actual_tick - self.high_active_tick  < self.min_high_active_tick:
                        message = "Estuvo parece una subida agresiva! Compra"
                        #self.check_buy_conditions = True
                        self.orderActive =  True
                        self.buy_price_close = actual_price 
                        self.buy_tick_time = self.actual_tick
                        self.do_long(message)
                '''
                        
                # otra estraegia se puede manejar independeinte
                '''
                if self.low_by_bands == True:
                    do_operation_buy = self.check_low_bands(filter_price["value"])
                    if do_operation_buy == True:
                        message = "Cambio de banda en low. Bajo de banda y toco el top de la superior!"
                        #self.check_buy_conditions = True
                        self.orderActive =  True
                        self.buy_price_close = actual_price
                        self.do_long(message)
                '''

                '''
                elif actual_price >= (self.high_upper + self.elastic_margin_high) and self.high_active == True:
                    message = "Parece una subida estrepitosa paso todos los High! Compra"
                    self.do_long(message)
                '''
                # esta estraegia no import si toco high
                # en caso de que toco la minima estimacion low (sin contar delta)
                # y el promedio subre, realiza compra
                '''
                if self.actual_tick <= (self.mean_tick * 0.6):
                    if actual_price <= self.low_lowwer and self.active_lower == False:
                        self.active_lower = True
                    if self.active_lower == True:
                        # actualiza el lower en caso de estar en baja
                        if actual_price < self.low_lowwer:
                            self.low_lowwer = actual_price
                        elif filter_price["value"] >= self.low_lowwer + self.cota_superior_lower:
                            message = "Toco el estimador mas chico, y sbuio. Compra agressive"
                            succes_order = self.do_long(message)
                            if succes_order == True:
                                self.made_lower_buy = True
                '''
                
            # busca venta
            else:
                # deja un lapso antes de ejecutar la compra
                #if self.check_buy_conditions == True:
                    # se asegura que no se toco high en este trayecto
                    # certifica si no toco high
                #    if self.touch_high == False:
                #        self.touch_high = self.is_high(actual_price)
                #        if self.touch_high == True:
                #            message = "Dentro de la espera de verificacion para hacer el trade Toca high antes que Low estimation en $ " + str(actual_price) + ". Ya no realiza trade."
                #            self.log(message,  to_ui = True, date = self.datetime[0])
                #            self.refresh_variables()
                    
                #    if self.touch_high == False:
                        # se asegura que al momento de hacer la compra la proyeccion minima supero lo esperado
                #        if  self.minimum_profit_estimation(actual_price, self.check_buy_high) and (filter_price["value"] - self.buy_price_close) >= self.check_buy_conditions_buy_conditions_value_high and self.actual_tick <= (self.mean_tick * self.max_ticks_to_operate):
                            # ahora si confirma compra.
                #            self.check_buy_conditions = False
                #            self.do_long(self.message)
                #            self.log("Supero cota de check con " + str(filter_price["value"] - self.buy_price_close),  to_ui = True, date = self.datetime[0])
                #        elif (self.buy_price_close - filter_price["value"] ) >= self.check_buy_conditions_buy_conditions_value_low:
                #            self.check_buy_conditions = False
                #            self.log("No supero cota de check con " + str(filter_price["value"] - self.buy_price_close) + " y no ejecuta",  to_ui = True, date = self.datetime[0])
                #            self.refresh_variables()
                
                #else:       
                    # si primero llega a una cota inferior negativa no la ejecuta y limpia todas las variables
                    # si primero llega a una cota superior positiva y cumple los requerimientos de tiempo (touch high no, porque ya puede haber alcansado)
                    # vende dinamico. Apunta a las crecidas marcadas y estrategia que funciona bien cuando el Bitcoin esta en suba.

                    # lower strategy es agressive
                '''
                if self.last_operation != "SELL":
                    if self.active_lower == True and self.made_lower_buy == True:
                        if actual_price - self.buy_price_close >= self.fixed_limit_high_lower:
                            message = "Llego minio high de $" + str(actual_price - self.buy_price_close) + ". Vende con ganancia minima! Lower strategy,  Lento pero seguro."
                            self.do_short(message)
                        elif self.buy_price_close - actual_price >= self.stoploss_lower:
                            message = "Llego a un stop loss lower de $" + str(self.buy_price_close - actual_price) + ". Vende con perdida."
                            self.do_short(message)
                '''
                # primer punto de inflexion con ganancia cierra
                '''
                if self.last_operation != "SELL":
                    if self.filter_price_is_inflection == True:
                        if filter_price["value"] > self.active_elastic_high: 
                            self.active_elastic_high = filter_price["value"]
                        if self.is_active_elastic_high == False:
                            self.is_active_elastic_high = True
                            if actual_price - self.buy_price_close > self.first_inflection_point_min_revenue:
                                message = "El primer punto de inflexion es mayor que 100,   Vende!."
                                self.do_short(message)
                '''
                # hard limit high
                '''
                if self.last_operation != "SELL":
                    if actual_price - self.buy_price_close >= self.fixed_limit_high:
                        message = "Llego minio high de $" + str(actual_price - self.buy_price_close) + ". Vende con ganancia minima! Lento pero seguro."
                        self.do_short(message)
                '''


                #dynamic high limit # first version sin filtro #
                if self.last_operation != "SELL":
                    if (self.buy_price_close - filter_price["value"]  > self.min_gain_dynamic):
                        if self.first_time_min_gain == False:
                            self.first_time_min_gain = True
                        self.min_gain_dynamic =  self.buy_price_close - filter_price["value"]
                
                    if self.first_time_min_gain == True:
                        if filter_price["value"] - ( self.buy_price_close -  self.min_gain_dynamic )   > self.delta_stop_loss_high:
                            message = "Bajo desde la ultima ganancia dinamica  " + str(self.buy_price_close - self.min_gain_dynamic) + " bajo diferencia de " + str(self.delta_stop_loss_high) + " y vende!"
                            self.do_short(message)
                    
                # stop loss filter average este es en caso que desde la compra no actualiza y va a perdida
                if self.last_operation != "SELL":
                    if filter_price["value"] - self.buy_price_close >= self.stoploss:
                        message = "Llego a un stop loss de $" + str(filter_price["value"] - self.buy_price_close) + ". Compra con perdida con perdida."
                        self.do_short(message)
                        
                '''
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
                '''

                if self.last_operation != "SELL":
                    if self.actual_tick >= (self.mean_tick - 10):
                        message = "esta llegando close y no toco low. ejecuta compra"
                        self.do_short(message)
        
        if len(self.data1.low) > self.lendata1:
            self.lendata1 += 1
            self.actual_tick = 0

            #print("Cada cambio de Vela de " + str(self.candle_min)  + " min")
            #print(self.data1.low[0])
            
            # low  = self.datas[1].low[0]
            # high = self.datas[1].high[0]
            # self.log('Low : %.3f %% '  % low)
            #self.log('High 1 min tick : %.3f %% '  % high)
            #self.log('Low data1: %.3f %% '  % float(self.data1.low[0]))
            # self.log('Low -1 data1: %.3f %% '  % float(self.data1.low[-1]))

            # en produccion ya tiene los datos cargados con historial
            # llama a buscar los indicadores ya estan cargados los lags.
            if ENV == PRODUCTION or self.STANDALONE == True:
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
                if ENV == PRODUCTION and  TESTING_PRODUCTION == False and self.STANDALONE == False and UPDATE_PARAMS_FUERZA_BRUTA == True:
                    if self.second_candle == False:
                        self.second_candle = True
                        self.previous_candle_last_tick_date = self.datetime[0]
                    else:
                        asyncio.run(self.update_fuerza_bruta(self.previous_candle_last_tick_date, self.datetime[0]))
                        
    async def update_fuerza_bruta(self, _from,_to):
        optimal_last_params = self.elasticLowBandOverlapHighFuerzaBruta.get_best_values(_from, _to)
        self.update_params_fuerza_bruta(optimal_last_params)

    def update_params_fuerza_bruta(self, params):
        self.stoploss = params["stoploss"]
        self.cota_superior_low = params["cota_superior_low"] 
        self.elastic_margin_low = params["elastic_margin_low"]
        self.fixed_limit_high = params["fixed_limit_high"] 
        self.minimum_profit_proyected = self.fixed_limit_high
        self.index_high_estimation = params["index_high_estimation"]
        self.mean_filter_lag = params["mean_filter_lag"] 
        self.touch_high_cota = params["touch_high_cota"] 
        #Log
        self.log("Actualiza parametros best strategy last -  stoploss: " + str(self.stoploss) + " - cota_superior_low: " + str(self.cota_superior_low),  to_ui = True, date = self.datetime[0])
        self.log("elastic_margin_low:" + str(self.elastic_margin_low) + " - fixed_limit_high: " + str(self.fixed_limit_high),  to_ui = True, date = self.datetime[0])
        self.log("index high estimation:" + str(self.index_high_estimation) + " - mean_filter_lag: " + str(self.mean_filter_lag),  to_ui = True, date = self.datetime[0])
        self.log("touch_high_cota" + str(self.touch_high_cota) ,  to_ui = True, date = self.datetime[0])
        self.log("El mejor balance de la vela anterior con estos parametros fue " + str(params["balance"]) ,  to_ui = True, date = self.datetime[0])



