#!/usr/bin/env python3

import time
import datetime
import backtrader as bt
import datetime as dt

from ccxtbt.ccxtstore import CCXTStore
from config import BINANCE, ENV, PRODUCTION, DEVELOPMENT, COIN_TARGET, COIN_REFER, DEBUG, STRATEGY, TESTING_PRODUCTION, LIVE
from messages import MESSAGE_TELEGRAM

from dataset.dataset import CustomDataset
from dataset.dataset_live import CustomDatasetLive
from sizer.percent import FullMoney

#from strategies.mediaEstimadoresDinamica import MediaEstimadoresDinamica
#from strategies.elasticLowBandOverlapHigh import ElasticLowBandOverlapHigh
#from strategies.elasticHighToLowBand import ElasticHighToLowBand
from strategies.simpleHighToLowMean3V2 import SimpleHighToLowMean3V2
##from strategies.elasticLowBandOverlapHighFuerzaBruta import ElasticLowBandOverlapHighFuerzaBruta
from strategies.simpleHighToLowMean3FuerzaBruta import SimpleHighToLowMean3FuerzaBruta

#from strategies.overlapHighEstimators import OverlapHighEstimators
#from strategies.dynamicHighStopLossLong import DynamicHighStopLossLong
#from strategies.dynamicStopLossLong import DynamicStopLossLong
# for test
from strategies.basic import Basic
from strategies.subidaEstrepitosaNeuralNetworkLive import SubidaEstrepitosaNeuralNetworkLive

from utils import print_trade_analysis, print_sqn, send_telegram_message, copy_UI_template

from production.cerebro import CerebroProduction
from production.broker import BrokerProduction
import websocket, json, pprint, numpy


def main():

    # template donde se guardan los resultados de la sessions y graficos. 
    #TODO conectar  creacion d Json a este link cuando este terminado parser JS.-
    # copy_UI_template()

    cerebro = bt.Cerebro(quicknotify=True)

    if ENV == PRODUCTION:  # Live trading with Binance
        kline_production = STRATEGY.get("kline_interval")  
        cerebro = CerebroProduction()
        broker_config = {
            'apiKey': BINANCE.get("key"),
            'secret': BINANCE.get("secret")
        }
        broker = BrokerProduction(broker_config,kline_production)
        cerebro.setbroker(broker)

        # hist_start_date = dt.datetime.utcnow() - dt.timedelta(minutes=30000)
        # data = store.getdata(
        #     dataname='%s/%s' % (COIN_TARGET, COIN_REFER),
   

    else:  # Backtesting with CSV file
        
        data = CustomDataset(
            name = COIN_TARGET,
            dataname = "dataset/databases/BTCUSDT-1m.csv",
            timeframe = bt.TimeFrame.Minutes,
            fromdate = datetime.datetime(2020, 12, 28),
            #fromdate = datetime.datetime(2021, 1, 26),
            #todate = datetime.datetime(2021, 2, 28),
            todate = datetime.datetime(2021, 3, 26),
            #todate = datetime.datetime(2021, 2, 26),
            nullvalue = 0.0
        )
        
        '''
        data = CustomDatasetLive(
            name = COIN_TARGET,
            dataname = "dataset/databases/BTCUSDT-milliseconds_1614320462088_1614348719999.csv",
            timeframe = bt.TimeFrame.Seconds,
            dtformat='%Y-%m-%d %H:%M:%S.%f',
            compression=2,
            #fromdate = datetime.datetime(2020, 12, 28),
            #todate = datetime.datetime(2021, 1, 10),
            nullvalue = 0.0
        )
        '''
        cerebro.adddata(data)
        # Resample to have multiple data like Binance. Compression x30, x60, x240, min. 
        second_time_frame = 30
        cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, 
                             compression=second_time_frame)
        broker = cerebro.getbroker()
        broker.setcommission(commission=0.001, name=COIN_TARGET)  # Simulating exchange fee
        broker.setcash(1000.0)
        cerebro.addsizer(FullMoney)

    # Analyzers to evaluate trades and strategies
    # SQN = Average( profit / risk ) / StdDev( profit / risk ) x SquareRoot( number of trades )
    #cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    #cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

    # # Include Strategy
    if ENV == PRODUCTION:
        strategy = SimpleHighToLowMean3V2()
        fuerza_bruta = SimpleHighToLowMean3FuerzaBruta()
        strategy.elasticLowBandOverlapHighFuerzaBruta = fuerza_bruta
        #strategy = OverlapHighEstimators()
        cerebro.addstrategy(strategy)
        if TESTING_PRODUCTION == False:
            cerebro.getHistoricalData(kline_production,3)
    else:
        cerebro.addstrategy(SubidaEstrepitosaNeuralNetworkLive)

    # # Starting backtrader bot
    # initial_value = cerebro.broker.getvalue()
    # print('Starting Portfolio Value: %.2f' % initial_value)
    if ENV == PRODUCTION:
        message_init =  MESSAGE_TELEGRAM.get("init_session")
        send_telegram_message(message_init)
    result = cerebro.run(stdstats=False)

    # if ENV == PRODUCTION:
    #     ws.run_forever()

    # # Print analyzers - results
    # final_value = cerebro.broker.getvalue()
    # print('Final Portfolio Value: %.2f' % final_value)
    # print('Profit %.3f%%' % ((final_value - initial_value) / initial_value * 100))
    # #  print_trade_analysis(result[0].analyzers.ta.get_analysis())
    # #  print_sqn(result[0].analyzers.sqn.get_analysis())

    if DEBUG and ENV == DEVELOPMENT:
        cerebro.plot()

if __name__ == "__main__":
    try:
        if LIVE == True:
            print("Las operaciones oficiales en Binance estan habilitadas, escribir 1 para contiunar.")
            confirm_live = input()
            if int(confirm_live) == 1:
                main()
            else:
                print("Por favor cambiar la configuracion para ejcutar en otra modalidad.")
        else:
            main()        
    except KeyboardInterrupt:
        print("finished.")
        time = dt.datetime.now().strftime("%d-%m-%y %H:%M")
        send_telegram_message("Bot finished by user at %s" % time)
    except Exception as err:
        send_telegram_message("Bot finished with error: %s" % err)
        print("Finished with error: ", err)
        raise
