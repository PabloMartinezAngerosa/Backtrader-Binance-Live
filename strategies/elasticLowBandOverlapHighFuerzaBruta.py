
#!/usr/bin/env python3

#import time
#import datetime
#import backtrader as bt
#import datetime as dt

#from ccxtbt.ccxtstore import CCXTStore
from config import BINANCE, ENV, PRODUCTION, DEVELOPMENT, COIN_TARGET, COIN_REFER, DEBUG, STRATEGY, TESTING_PRODUCTION, SANDBOX_INITAL_CAPITAL
from utils import send_telegram_message
#from messages import MESSAGE_TELEGRAM
from multiprocessing import Pool

#from dataset.dataset import CustomDataset
#from dataset.dataset_live import CustomDatasetLive
#from sizer.percent import FullMoney

from strategies.elasticLowBandOverlapHigh import ElasticLowBandOverlapHigh


#from utils import print_trade_analysis, print_sqn, send_telegram_message, copy_UI_template

from production.cerebro import CerebroProduction
from production.broker import BrokerProduction
#import websocket, json, pprint, numpy




class ElasticLowBandOverlapHighFuerzaBruta():
    def __init__(self, generate_CSV = False):
        '''
            params: 
                _from ~ desde el tick en BD inicial
                _to ~ hasta el tick en BD 
        '''
        self._from = None
        self._to = None
        self.generate_CSV = generate_CSV
        # se establecen los parametros y rangos
        # descripcion de que automatizar
        
        #  se mide en negativo. se pensaba que subia, pero baja. cuando supera cancela y vuelve a comprar
        # con esa perdida. 
        self.stoploss = [25, 50, 80, 120]
        # desde la peor estimacion del low, aumenta una banda para considerar que esta activa.
        self.cota_superior_low = [10,30,50]
        # una vez que la banda quedo activa, si se separa de la cota superior por este valor, compra
        self.elastic_margin_low = [5,15,30]
        # marca un fijo de ganacia y frena
        self.fixed_limit_high = [140,200,280]
        # limite de indicador, mean que compara para saber si cumple la proyecction minima mean1, mean2, mean3
        self.index_high_estimation = [1,2,3]
        # filtro lags
        self.mean_filter_lag = [2,5,15]
        # cota superior para decir q toco high prediction
        self.touch_high_cota = [15,50,80]
        # limite para certificar acciones espera para comprar
        self.check_buy_conditions_buy_conditions_value_high = [20,30,40,50,60,70,80,90]
        # limite para certificar que en realidad va a perdiad
        self.check_buy_conditions_buy_conditions_value_low = [30,40,50,60,70,80,90,100]



    def get_best_estrategy_params(self, _from, _to, index_multicore):
        '''
           Hace por fuerza bruta todas las posibles opcoines en grillas de valores discretos
           que es establecida en el header.
           Esta funcion esta optimizada para 4 cores. Es importante actuailizar
           el codigo en caso de tener mas cores. 
        '''
        self._from = _from
        self._to = _to
        results = []
        fields = []
        total_fields = 8*8*11
        counter = 0
        kline_production = STRATEGY.get("kline_interval")
        broker_config = {
            'apiKey': BINANCE.get("key"),
            'secret': BINANCE.get("secret")
        }
        broker = BrokerProduction(broker_config,kline_production, stand_alone = True)
        data_tick = broker.sql_cache.get_ticks_realtime(self._from, self._to)
        for i in range(2):
            index = i + index_multicore
            range_check_high = self.check_buy_conditions_buy_conditions_value_high[index]
            for range_check_low in self.check_buy_conditions_buy_conditions_value_low:
                for range_fixed_limit_high in self.fixed_limit_high:
                    cerebro = CerebroProduction()
                    # broker = BrokerProduction(broker_config,kline_production, stand_alone = True)
                    cerebro.setbroker(broker)
                    strategy = ElasticLowBandOverlapHigh(stand_alone = True)
                    strategy.check_buy_conditions_buy_conditions_value_high = range_check_high
                    strategy.check_buy_conditions_buy_conditions_value_low = range_check_low
                    strategy.fixed_limit_high = range_fixed_limit_high
                    cerebro.addstrategy(strategy)
                    cerebro.getbroker().simulate_binance_socket(data_tick)
                    # cerebro get profit devuelve un objeto con el total de trades, trades gananica, trades lost, y el profit generado, maxima perdidas
                    final_capital = cerebro.get_wallet_balance()
                    results.append(final_capital)
                    fields.append({
                        "balance" : final_capital,
                        "check_buy_conditions_buy_conditions_value_high" : range_check_high,
                        "check_buy_conditions_buy_conditions_value_low" : range_check_low,
                        "fixed_limit_high" : range_fixed_limit_high
                    })
                    counter = counter + 1
                    #send_telegram_message("El maximo hasta el momento es " + str(max(results)) + " , el actual es " +  str(final_capital)+ ", " + str((counter*100) /total_fields))
                    print( str((counter*100) /total_fields) + "%" )

        #print(fields)

        max_balance = max(results)
        values = {
            "max" : max_balance,
            "values" : fields
        }
        '''
        check_buy_conditions_buy_conditions_value_high = []
        check_buy_conditions_buy_conditions_value_low = []
        fixed_limit_high = []

        for result in fields:
            if result["balance"] == max_balance:
                check_buy_conditions_buy_conditions_value_high.append(result["check_buy_conditions_buy_conditions_value_high"])
                check_buy_conditions_buy_conditions_value_low.append(result["check_buy_conditions_buy_conditions_value_low"])
                fixed_limit_high.append(result["fixed_limit_high"])
        optimal_values =  {
            "check_buy_conditions_buy_conditions_value_high" : sum(check_buy_conditions_buy_conditions_value_high)/len(check_buy_conditions_buy_conditions_value_high),
            "check_buy_conditions_buy_conditions_value_low" : sum(check_buy_conditions_buy_conditions_value_low)/len(check_buy_conditions_buy_conditions_value_low),
            "fixed_limit_high" : sum(fixed_limit_high)/len(fixed_limit_high)
        }
                
        #print("Con un capital inicial de " + str(SANDBOX_INITAL_CAPITAL) + " el retorno maximo final es de " + str(max(results)))
        ''' 
        return values


    def get_best_estrategy_params_all(self, _from, _to, index_multicore):
        self._from = _from
        self._to = _to
        results = []
        fields = []
        total_fields = 3*3*3*3*3*3
        counter = 0
        kline_production = STRATEGY.get("kline_interval")
        broker_config = {
            'apiKey': BINANCE.get("key"),
            'secret': BINANCE.get("secret")
        }
        broker = BrokerProduction(broker_config,kline_production, stand_alone = True)
        data_tick = broker.sql_cache.get_ticks_realtime(self._from, self._to)
        for range_cota_superior_low in self.cota_superior_low:
            for range_elastic_margin_low in self.elastic_margin_low:
                for range_fixed_limit_high in self.fixed_limit_high:
                    for range_index_high_estimation in self.index_high_estimation:
                        for range_mean_filter_lag in self.mean_filter_lag:
                            for range_touch_high_cota in self.touch_high_cota:
                                cerebro = CerebroProduction()
                                # broker = BrokerProduction(broker_config,kline_production, stand_alone = True)
                                cerebro.setbroker(broker)
                                strategy = ElasticLowBandOverlapHigh(stand_alone = True)
                                strategy.stoploss = self.stoploss[index_multicore]
                                strategy.cota_superior_low = range_cota_superior_low
                                strategy.elastic_margin_low = range_elastic_margin_low
                                strategy.fixed_limit_high = range_fixed_limit_high
                                strategy.index_high_estimation = range_index_high_estimation
                                strategy.mean_filter_lag = range_mean_filter_lag
                                strategy.touch_high_cota = range_touch_high_cota
                                cerebro.addstrategy(strategy)
                                cerebro.getbroker().simulate_binance_socket(data_tick)
                                # cerebro get profit devuelve un objeto con el total de trades, trades gananica, trades lost, y el profit generado, maxima perdidas
                                final_capital = cerebro.get_wallet_balance()
                                results.append(final_capital)
                                fields.append({
                                    "balance" : final_capital,
                                    "stoploss" : self.stoploss[index_multicore],
                                    "cota_superior_low" : range_cota_superior_low,
                                    "elastic_margin_low" : range_elastic_margin_low,
                                    "fixed_limit_high" : range_fixed_limit_high,
                                    "index_high_estimation" : range_index_high_estimation,
                                    "mean_filter_lag" : range_mean_filter_lag,
                                    "touch_high_cota" : range_touch_high_cota
                                })
                                counter = counter + 1
                                #send_telegram_message("El maximo hasta el momento es " + str(max(results)) + " , el actual es " +  str(final_capital)+ ", " + str((counter*100) /total_fields))
                                print( str((counter*100) /total_fields) + "%" )

        #print(fields)

        #print("Con un capital inicial de " + str(SANDBOX_INITAL_CAPITAL) + " el retorno maximo final es de " + str(max(results)))
        max_balance = max(results)
        values = {
            "max" : max_balance,
            "values" : fields
        }
        return values
        
        # realiza un for con cada uno de los parametros
        # cada una de las opciones
           # se genera una instancia de Cerebro,
           # se configura las variables de config necesarias
           # se obtiene ganancia y perdida
           # se guarda en dataframe las opciones variables ganancia y perdiad
        # se exporta el datframe como un CSV (opcional)
        # se retorna los valores de los parametros de la ganancia y pedida que de mejor resultado

    def multi_core_action(self, index):
        return self.get_best_estrategy_params_all(self._from, self._to, index)

    def get_best_values(self, _from, _to):
        self._from = _from
        self._to = _to
        p = Pool(4)
        values_multicore = p.map(self.multi_core_action, [0,1,2,3])
        max_balance = []
        for cores in values_multicore:
            max_balance.append(cores["max"])
        max_balance = max(max_balance)
        print("El valor maximo es " + str(max_balance))

        stoploss = []
        cota_superior_low = []
        elastic_margin_low = []
        fixed_limit_high = []
        index_high_estimation = []
        mean_filter_lag = []
        touch_high_cota = []


        for cores in values_multicore:
            fields = cores["values"]
            for result in fields:
                if result["balance"] == max_balance:
                    stoploss.append(result["stoploss"])
                    cota_superior_low.append(result["cota_superior_low"])
                    elastic_margin_low.append(result["elastic_margin_low"])
                    fixed_limit_high.append(result["fixed_limit_high"])
                    index_high_estimation.append(result["index_high_estimation"])
                    mean_filter_lag.append(result["mean_filter_lag"])
                    touch_high_cota.append(result["touch_high_cota"])
    
        optimal_values =  {
            "balance": max_balance, 
            "stoploss" : sum(stoploss)/len(stoploss),
            "cota_superior_low" : sum(cota_superior_low)/len(cota_superior_low),
            "elastic_margin_low" : sum(elastic_margin_low)/len(elastic_margin_low),
            "fixed_limit_high" : sum(fixed_limit_high)/len(fixed_limit_high),
            "index_high_estimation" : int(sum(index_high_estimation)/len(index_high_estimation)),
            "mean_filter_lag" : int(sum(mean_filter_lag)/len(mean_filter_lag)),
            "touch_high_cota" : sum(touch_high_cota)/len(touch_high_cota)
        }
        return optimal_values

