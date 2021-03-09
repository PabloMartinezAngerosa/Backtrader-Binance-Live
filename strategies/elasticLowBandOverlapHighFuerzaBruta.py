
#!/usr/bin/env python3

#import time
#import datetime
#import backtrader as bt
#import datetime as dt

#from ccxtbt.ccxtstore import CCXTStore
from config import BINANCE, ENV, PRODUCTION, DEVELOPMENT, COIN_TARGET, COIN_REFER, DEBUG, STRATEGY, TESTING_PRODUCTION, SANDBOX_INITAL_CAPITAL
from utils import send_telegram_message
#from messages import MESSAGE_TELEGRAM

#from dataset.dataset import CustomDataset
#from dataset.dataset_live import CustomDatasetLive
#from sizer.percent import FullMoney

from strategies.elasticLowBandOverlapHigh import ElasticLowBandOverlapHigh


#from utils import print_trade_analysis, print_sqn, send_telegram_message, copy_UI_template

from production.cerebro import CerebroProduction
from production.broker import BrokerProduction
#import websocket, json, pprint, numpy




class ElasticLowBandOverlapHighFuerzaBruta():
    def __init__(self, _from, _to, generate_CSV = False):
        '''
            params: 
                _from ~ desde el tick en BD inicial
                _to ~ hasta el tick en BD 
        '''
        self._from = _from
        self._to = _to
        self.generate_CSV = generate_CSV
        # se establecen los parametros y rangos
        # descripcion de que automatizar
        
        #  se mide en negativo. se pensaba que subia, pero baja. cuando supera cancela y vuelve a comprar
        # con esa perdida. 
        self.stoploss = [50, 80, 120]
        # desde la peor estimacion del low, aumenta una banda para considerar que esta activa.
        self.cota_superior_low = [10,30,50]
        # una vez que la banda quedo activa, si se separa de la cota superior por este valor, compra
        self.elastic_margin_low = [5,15,30]
        # marca un fijo de ganacia y frena
        self.fixed_limit_high = [140,190,250]
        # profit minimo q establece como limite para entrar
        self.minimum_profit_proyected = [70,140,190]
        # filtro lags
        self.mean_filter_lag = [2,5,15]
        # cota superior para decir q toco high prediction
        self.touch_high_cota = [15,50,80]




    def get_best_estrategy_params(self):
        results = []
        fields = []
        total_fields = 3**7
        counter = 0
        kline_production = STRATEGY.get("kline_interval")
        broker_config = {
            'apiKey': BINANCE.get("key"),
            'secret': BINANCE.get("secret")
        }
        broker = BrokerProduction(broker_config,kline_production, stand_alone = True)
        data_tick = broker.sql_cache.get_ticks_realtime(self._from, self._to)
        for range_stoploss in self.stoploss:
            for range_cota_superior_low in self.cota_superior_low:
                for range_elastic_margin_low in self.elastic_margin_low:
                    for range_fixed_limit_high in self.fixed_limit_high:
                        for range_minimum_profit_proyected in self.minimum_profit_proyected:
                            for range_mean_filter_lag in self.mean_filter_lag:
                                for range_touch_high_cota in self.touch_high_cota:
                                    cerebro = CerebroProduction()
                                    # broker = BrokerProduction(broker_config,kline_production, stand_alone = True)
                                    cerebro.setbroker(broker)
                                    strategy = ElasticLowBandOverlapHigh(stand_alone = True)
                                    strategy.stoploss = range_stoploss
                                    strategy.cota_superior_low = range_cota_superior_low
                                    strategy.elastic_margin_low = range_elastic_margin_low
                                    strategy.fixed_limit_high = range_fixed_limit_high
                                    strategy.minimum_profit_proyected = range_minimum_profit_proyected
                                    strategy.mean_filter_lag = range_mean_filter_lag
                                    strategy.touch_high_cota = range_touch_high_cota
                                    cerebro.addstrategy(strategy)
                                    cerebro.getbroker().simulate_binance_socket(data_tick)
                                    # cerebro get profit devuelve un objeto con el total de trades, trades gananica, trades lost, y el profit generado, maxima perdidas
                                    final_capital = cerebro.get_wallet_balance()
                                    results.append(final_capital)
                                    fields.append({
                                        "balance" : final_capital,
                                        "stoploss" : range_stoploss,
                                        "cota_superior_low" : range_cota_superior_low,
                                        "elastic_margin_low" : range_elastic_margin_low,
                                        "fixed_limit_high" : range_fixed_limit_high,
                                        "minimum_profit_proyected" : range_minimum_profit_proyected,
                                        "mean_filter_lag" : range_mean_filter_lag,
                                        "touch_high_cota" : range_touch_high_cota
                                    })
                                    counter = counter + 1
                                    send_telegram_message("El maximo hasta el momento es " + str(max(results)) + " , el actual es " +  str(final_capital)+ ", " + str((counter*100) /total_fields))
                                    print( str((counter*100) /total_fields) + "%" )

        print(fields)

        print("Con un capital inicial de " + str(SANDBOX_INITAL_CAPITAL) + " el retorno maximo final es de " + str(max(results)))

        
        # realiza un for con cada uno de los parametros
        # cada una de las opciones
           # se genera una instancia de Cerebro,
           # se configura las variables de config necesarias
           # se obtiene ganancia y perdida
           # se guarda en dataframe las opciones variables ganancia y perdiad
        # se exporta el datframe como un CSV (opcional)
        # se retorna los valores de los parametros de la ganancia y pedida que de mejor resultado


