#!/usr/bin/env python3

import time
import datetime
import backtrader as bt
import datetime as dt

from ccxtbt.ccxtstore import CCXTStore
from config import BINANCE, ENV, PRODUCTION, DEVELOPMENT, COIN_TARGET, COIN_REFER, DEBUG

from dataset.dataset import CustomDataset
from sizer.percent import FullMoney
from strategies.dynamicStopLossLong import DynamicStopLossLong
# for test
from strategies.basic import Basic

from utils import print_trade_analysis, print_sqn, send_telegram_message

from production.cerebro import CerebroProduction
from production.broker import BrokerProduction
import websocket, json, pprint, talib, numpy


def main():
    cerebro = bt.Cerebro(quicknotify=True)

    if ENV == PRODUCTION:  # Live trading with Binance
        
        cerebro = CerebroProduction()
        broker_config = {
            'apiKey': BINANCE.get("key"),
            'secret': BINANCE.get("secret")
        }
        broker = BrokerProduction(broker_config)
        cerebro.setbroker(broker)

        # hist_start_date = dt.datetime.utcnow() - dt.timedelta(minutes=30000)
        # data = store.getdata(
        #     dataname='%s/%s' % (COIN_TARGET, COIN_REFER),
   

    else:  # Backtesting with CSV file
        data = CustomDataset(
            name = COIN_TARGET,
            dataname = "dataset/BTCUSDT-1m.csv",
            timeframe = bt.TimeFrame.Minutes,
            fromdate = datetime.datetime(2021, 1, 2),
            todate = datetime.datetime(2021, 1, 10),
            nullvalue = 0.0
        )
        cerebro.adddata(data)
        # Resample to have multiple data like Binance. Compression x30, x60, x240, min. 
        second_time_frame = 30
        cerebro.resampledata(data, timeframe=bt.TimeFrame.Minutes, 
                             compression=second_time_frame)
        broker = cerebro.getbroker()
        broker.setcommission(commission=0.001, name=COIN_TARGET)  # Simulating exchange fee
        broker.setcash(100000.0)
        cerebro.addsizer(FullMoney)

    # Analyzers to evaluate trades and strategies
    # SQN = Average( profit / risk ) / StdDev( profit / risk ) x SquareRoot( number of trades )
    #cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    #cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

    # # Include Strategy
    if ENV == PRODUCTION:
        strategy = DynamicStopLossLong()
        cerebro.addstrategy(strategy)
        cerebro.getHistoricalData()
    else:
        cerebro.addstrategy(Basic)

    # # Starting backtrader bot
    # initial_value = cerebro.broker.getvalue()
    # print('Starting Portfolio Value: %.2f' % initial_value)
    result = cerebro.run()

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
        main()
    except KeyboardInterrupt:
        print("finished.")
        time = dt.datetime.now().strftime("%d-%m-%y %H:%M")
        send_telegram_message("Bot finished by user at %s" % time)
    except Exception as err:
        send_telegram_message("Bot finished with error: %s" % err)
        print("Finished with error: ", err)
        raise
