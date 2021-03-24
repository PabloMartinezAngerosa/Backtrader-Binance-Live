# #!/usr/bin/env python3

import backtrader as bt

from config import ENV, PRODUCTION, STRATEGY, TESTING_PRODUCTION, LIVE, UPDATE_PARAMS_FUERZA_BRUTA
from strategies.base import StrategyBase
from binance.enums import *
import asyncio



class SimpleHighToLowMean3(StrategyBase):

    # Moving average parameters
    # params = (('pfast',20),('pslow',50),)

    def __init__(self, stand_alone = False):
        StrategyBase.__init__(self, stand_alone = stand_alone)

        # apuesta a la baja
        self.sell_and_buy_strategy = True
        
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
        self.media_high_reference = 1 # 1: mean, 2: mean-2, 3: mean-3
        self.media_low_reference = 1 # 1: mean, 2: mean-2, 3: mean-3
        self.touch_low_cota = 30
        self.max_ticks_to_operate = 0.35 # aggressive operation en inicio
        self.min_gain = 180 # punto en el cual ejecuta dynamic
        self.min_lost = 120
        self.cota_inferior_high = 15 # necesita confirmar de menos 30 en los ticks correspondientes para dar el ok 
        self.ticks_to_wait = 10 # ticks q espera para confirmar baja

        self.delta_error_estimacion_high = 15
        self.rmse_estimadores = 75
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
        
        self.min_gain_dynamic = self.min_gain 
        self.low_by_bands = True
        
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
        self.touch_low = False
        self.active_lower = False
        self.low_band_active_value = 0
        self.low_band_active = False
        self.check_buy_conditions = False
        self.second_candle = False
        self.previous_candle_last_tick_date = 0
        self.first_time_min_gain = False
        self.buy_tick_time = 0
        self.active_high_mean3 = False
        self.active_tick = 0
        
        
    
    def get_high_low(self):
        # los indicadores estan de menor a mayor
        # se busca el valor mas chico
        high_low = 0
        for low_estimation in self.ensambleIndicators.indicatorsLow:
            if low_estimation > high_low and low_estimation < self.open_candle:
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
        self.touch_low = False
        self.low_band_active = False
        self.low_band_active_value = 0
        self.check_buy_conditions = False
        self.min_gain_dynamic = self.min_gain
        self.first_time_min_gain = False
        self.buy_tick_time = 0
        self.active_high_mean3 = False
        self.active_tick = 0
    
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
    
    def get_mean_low_reference(self):
        if self.media_low_reference ==1:
            return self.ensambleIndicators.mediaEstimadorLow 
        elif self.media_low_reference ==2:
            return self.ensambleIndicators.mediaEstimadorLow_iterada2
        elif self.media_low_reference ==3:
            return self.ensambleIndicators.mediaEstimadorLow_iterada3
        else:
            return self.ensambleIndicators.mediaEstimadorLow
    
    def get_mean_high_reference(self):
        if self.media_high_reference ==1:
            return self.ensambleIndicators.mediaEstimadorHigh
        elif self.media_high_reference ==2:
            return self.ensambleIndicators.mediaEstimadorHigh_iterada2
        elif self.media_high_reference ==3:
            return self.ensambleIndicators.mediaEstimadorHigh_iterada3
        else:
            return self.ensambleIndicators.mediaEstimadorHigh

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
                #TODO DANGER cuidado esta alrevez solo para esta estrategia corregir DANGER
                succces_trade = self.broker.order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
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
                #TODO DANGER cuidado esta alrevez solo para esta estrategia corregir DANGER
                succces_trade = self.broker.order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
            if succces_trade == True:
                self.log(message,  to_ui = True, date = self.datetime[0])
                self.sell_order()
                return True
        return False

    def is_low(self, actual_price):
        #for low_estimation in self.ensambleIndicators.indicatorsLow:
        if (self.ensambleIndicators.mediaEstimadorLow + self.rmse_estimadores) >= actual_price:
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
                if self.touch_low == False:
                    self.touch_low = self.is_low(actual_price)
                    if self.touch_low == True:
                        message = "Toca low antes que High estimation en $ " + str(actual_price) + ". Ya no realiza trade. Dynamic Params high: " + str(self.media_high_reference) + ", low:"+ str(self.media_low_reference)
                        self.log(message,  to_ui = True, date = self.datetime[0])

                if self.touch_low == False:
                    # pone en modo activo y deja pasar unos 15, 20 ticks. 
                    # si no pasa 30 USD no ejecuta. Se vuelve a activar hasta tocar un low.
                    # upper low aggresive
                    if self.actual_tick <= (self.mean_tick * self.max_ticks_to_operate):
                        # elsastic band low, utiliza el filtro para asegurar q no son picos. 
                        if actual_price >= self.get_mean_high_reference() - self.delta_error_estimacion_high:
                            self.active_high_mean3 = True
                            self.active_tick = self.actual_tick
                
                if self.active_high_mean3 == True:
                    if self.actual_tick - self.active_tick >= self.ticks_to_wait:
                        if actual_price <= self.get_mean_high_reference() - self.cota_inferior_high - self.delta_error_estimacion_high:
                            message = "toco literalmente high mean 3 a la baja , Compra! Dynamic Params high: " + str(self.media_high_reference) + ", low:"+ str(self.media_low_reference)
                            #self.check_buy_conditions = True
                            self.orderActive =  True
                            self.buy_price_close = actual_price 
                            self.min_gain_dynamic = self.buy_price_close - self.get_mean_low_reference() 
                            self.buy_tick_time = self.actual_tick
                            self.do_long(message)
                        else:
                            message = "Pasaron los ticks y no alcanzo la baja suficiente. Vuelve a actualizar por si hay otra baja. Dynamic Params high: " + str(self.media_high_reference) + ", low:"+ str(self.media_low_reference)
                            self.log(message,  to_ui = True, date = self.datetime[0])
                            self.active_high_mean3 = False

            # busca compra
            else:


                #dynamic high limit # first version sin filtro #
                if self.last_operation != "SELL":
                    if (self.buy_price_close - actual_price  > self.min_gain_dynamic):
                        if self.first_time_min_gain == False:
                            self.first_time_min_gain = True
                        self.min_gain_dynamic = self.buy_price_close - actual_price
                
                    if self.first_time_min_gain == True:
                        if filter_price["value"] - ( self.buy_price_close -  self.min_gain_dynamic )   > self.delta_stop_loss_high:
                            message = "Bajo desde la ultima ganancia dinamica  " + str(self.buy_price_close - self.min_gain_dynamic) + " bajo diferencia de " + str(self.delta_stop_loss_high) + " y vende!"
                            self.do_short(message)

                # version 1 dura. Fija en +-180 o va al final 
                
                if self.last_operation != "SELL":
                    '''
                    if (self.buy_price_close - actual_price  >= self.min_gain):
                        message = "Llego a un minimo fijo  " + str(self.buy_price_close - actual_price) + "  y vende!"
                        self.do_short(message)
                    
                    '''
                    if (actual_price - self.buy_price_close) >= self.min_lost:
                        message = "Llego a un stoploos fijo  " + str(self.buy_price_close - actual_price) + "  y vende!"
                        self.do_short(message)
                '''
                if self.last_operation != "SELL":
                    if (self.buy_price_close - actual_price  >= self.min_gain_dynamic):
                        if self.first_time_min_gain == False:
                            self.first_time_min_gain = True
                        self.min_gain_dynamic =  self.buy_price_close - filter_price["value"]
                
                    if self.first_time_min_gain == True:
                        if filter_price["value"] - ( self.buy_price_close -  self.min_gain_dynamic )   > self.delta_stop_loss_high:
                            message = "Bajo desde la ultima ganancia dinamica  " + str(self.buy_price_close - self.min_gain_dynamic) + " bajo diferencia de " + str(self.delta_stop_loss_high) + " y vende!"
                            self.do_short(message)
                '''
                    
                        
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
                if ENV == PRODUCTION and self.STANDALONE == False and UPDATE_PARAMS_FUERZA_BRUTA == True:
                    if self.second_candle == False:
                        self.second_candle = True
                        self.previous_candle_last_tick_date = self.datetime[0]
                    else:
                        asyncio.run(self.update_fuerza_bruta(self.previous_candle_last_tick_date, self.datetime[0]))
                        self.previous_candle_last_tick_date = self.datetime[0]
                        
    async def update_fuerza_bruta(self, _from,_to):
        optimal_last_params = self.elasticLowBandOverlapHighFuerzaBruta.get_best_values(_from, _to)
        self.update_params_fuerza_bruta(optimal_last_params)

    def update_params_fuerza_bruta(self, params):
        if params["balance"] > 1000:
            self.media_high_reference = params["media_high_reference"]
            self.media_low_reference = params["media_low_reference"] 
        

