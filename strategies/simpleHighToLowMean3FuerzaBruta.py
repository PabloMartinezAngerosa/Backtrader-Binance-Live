
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

from strategies.simpleHighToLowMean3 import SimpleHighToLowMean3


#from utils import print_trade_analysis, print_sqn, send_telegram_message, copy_UI_template

from production.cerebro import CerebroProduction
from production.broker import BrokerProduction
#import websocket, json, pprint, numpy




class SimpleHighToLowMean3FuerzaBruta():
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
        
        #  cual de los tres estimadores elige como referencia high
        self.media_high_reference = [1,2,3]
        # cual de los tres estimadores elige como referencia low
        self.media_low_reference = [1,2,3]



    def get_best_estrategy_params_all(self, _from, _to, index_multicore):
        self._from = _from
        self._to = _to
        results = []
        fields = []
        total_fields = 3*3
        counter = 0
        kline_production = STRATEGY.get("kline_interval")
        broker_config = {
            'apiKey': BINANCE.get("key"),
            'secret': BINANCE.get("secret")
        }
        broker = BrokerProduction(broker_config,kline_production, stand_alone = True)
        data_tick = broker.sql_cache.get_ticks_realtime(self._from, self._to)
        for range_media_low_reference in self.media_low_reference:           
            cerebro = CerebroProduction()
            # broker = BrokerProduction(broker_config,kline_production, stand_alone = True)
            cerebro.setbroker(broker)
            strategy = SimpleHighToLowMean3(stand_alone = True)
            strategy.media_high_reference = self.media_high_reference[index_multicore]
            strategy.media_low_reference = range_media_low_reference
            cerebro.addstrategy(strategy)
            cerebro.getbroker().simulate_binance_socket(data_tick)
            # cerebro get profit devuelve un objeto con el total de trades, trades gananica, trades lost, y el profit generado, maxima perdidas
            final_capital = cerebro.get_wallet_balance()
            results.append(final_capital)
            fields.append({
                "balance" : final_capital,
                "media_high_reference" : self.media_high_reference[index_multicore],
                "media_low_reference" : range_media_low_reference
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
        p = Pool(3)
        values_multicore = p.map(self.multi_core_action, [0,1,2])
        max_balance = []
        for cores in values_multicore:
            max_balance.append(cores["max"])
        max_balance = max(max_balance)
        print("El valor maximo es " + str(max_balance))

        media_high_reference = []
        media_low_reference = []


        for cores in values_multicore:
            fields = cores["values"]
            for result in fields:
                if result["balance"] == max_balance:
                    media_high_reference.append(result["media_high_reference"])
                    media_low_reference.append(result["media_low_reference"])
    
        optimal_values =  {
            "balance": max_balance, 
            "media_high_reference" : max(media_high_reference, key=media_high_reference.count),
            "media_low_reference" : max(media_low_reference, key=media_low_reference.count)
        }
        print("----------------------------------------------")
        print("optimal values last strategy:")
        print(optimal_values)
        return optimal_values

