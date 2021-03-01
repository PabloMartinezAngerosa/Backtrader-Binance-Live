#!/usr/bin/env python3

from datetime import datetime
import backtrader as bt
from termcolor import colored
from config import DEVELOPMENT, COIN_TARGET, COIN_REFER, ENV, PRODUCTION, DEBUG, STRATEGY
from utils import send_telegram_message
from production.strategy  import Strategy
from dataset.data_live import DataLive
from indicators.ensambleLinearRegressionAverage import EnsambleLinearRegressionAverage
from UI.jsonParser import JsonParser
# run_max.py
import subprocess



if ENV == PRODUCTION:
    bt.Strategy = Strategy


class StrategyBase(bt.Strategy):

    params = {'bufferSize':50}
    
    def __init__(self):
        
        # Para configurar lags y ancho de ventana de analisis  
        # default values. Se actualiza en cada estrategia
        self.ensambleIndicatorsLags = STRATEGY.get("lags")
        self.ensambleIndicatorsLengthFrames = STRATEGY.get("length_frames")
        self.candle_min = STRATEGY.get("candle_min")

        self.order = None
        self.last_operation = "SELL"
        self.status = "DISCONNECTED"
        self.bar_executed = 0
        self.buy_price_close = None
        self.sell_price_close = None
        self.timestamp_sell = None
        self.timestamp_buy = None
        self.soft_sell = False
        self.hard_sell = False
        self.log("Base strategy initialized")
        self.subClass = None
        self.ensambleIndicators = EnsambleLinearRegressionAverage(self.ensambleIndicatorsLags,self.ensambleIndicatorsLengthFrames)
        self.jsonParser = JsonParser(self.ensambleIndicators)

        if ENV == PRODUCTION:
            self.datas = []
            self.data0 = None
            self.data1 = None
            self.datetime = []

            data1 = DataLive()
            data2 = DataLive()
            
            self.datas.append(data1)
            self.datas.append(data2)

            self.update_data_internal()
    
    def updateIndicatorsEnsambleLinearModels(self):
        
        datetime = self.datetime[0]
        dataset = self.data1
        
        lags = self.ensambleIndicatorsLags
        lengths_frames = self.ensambleIndicatorsLengthFrames
        candle_min = self.candle_min
        self.ensambleIndicators.get_indicators(dataset, datetime, lags, lengths_frames, candle_min)
        self.jsonParser.create_json_file(self.ensambleIndicators)

    def add_tick( self, indexData, referenceObject, value, isDate = False):
        buffer = []
        if isDate == False:
            buffer.append(float(value))
        else:
            buffer.append(value)
        if len(referenceObject) == 0:
            return buffer
        elif len(referenceObject) == 1:
            buffer.append(referenceObject[0])
            return  buffer
        else:
            previousLastValue = referenceObject[0]
            betweenValues = referenceObject[1:len(referenceObject)]
            # Problem with live. TODO solve buffer live
            if indexData == 0:
                if (len(betweenValues)> self.params['bufferSize']):
                    betweenValues  = betweenValues[len(betweenValues) - self.params['bufferSize']:len(betweenValues)]
            for lag in  betweenValues:
                buffer.append(lag)
            buffer.append(previousLastValue)
            return buffer

    def add_next_frame_live(self, indexData, datatime, open, low, high, close, volume, next = True):
        if next == True:
            self.datetime = self.add_tick(0, self.datetime, datatime, True)
        self.datas[indexData].datetime = self.add_tick(indexData, self.datas[indexData].datetime, datatime, True)
        self.datas[indexData].open = self.add_tick(indexData, self.datas[indexData].open, open)
        self.datas[indexData].low = self.add_tick(indexData, self.datas[indexData].low, low)
        self.datas[indexData].high = self.add_tick(indexData, self.datas[indexData].high, high)
        self.datas[indexData].close = self.add_tick(indexData, self.datas[indexData].close, close)
        self.datas[indexData].volume = self.add_tick(indexData, self.datas[indexData].volume, volume)

        self.update_data_internal()
        if next == True:
            self.next()
        

    def update_data_internal(self):
        self.data0 = self.datas[0]
        self.data1 = self.datas[1]
    
    def reset_sell_indicators(self):
        self.soft_sell = False
        self.hard_sell = False
        self.sell_price_close = None
        self.timestamp_sell = None

    def reset_buy_indicators(self):
        self.buy_price_close = None
        self.timestamp_buy = None

    def notify_data(self, data, status, *args, **kwargs):
        self.status = data._getstatusname(status)
        print(self.status)
        if status == data.LIVE:
            self.log("LIVE DATA - Ready to trade")

    def short(self):
        if self.last_operation == "SELL":
            return
        self.sell_price_close = self.data0.close[0]
        self.timestamp_sell = self.datetime[0]
        if ENV == DEVELOPMENT:
            self.log("Sell ordered: $%.2f" % self.data0.close[0])
            return self.sell()
        if ENV == PRODUCTION:
            send_telegram_message(" \U0001F4E3 Orden de venta a : $%.2f" % self.data0.close[0])
            self.last_operation = "SELL"
            self.jsonParser.addSellOperation(self.timestamp_sell, 
                                self.sell_price_close, 
                                self.sell_price_close, 
                                0, 
                                0)
            delta_order = self.sell_price_close - self.buy_price_close
            self.jsonParser.addTrade(self.sell_price_close - self.buy_price_close, 0)
            if delta_order > 0:
                send_telegram_message(" \U0001F44C El trade fue exitoso! Con delta de : $%.2f" % delta_order)
            else:
                send_telegram_message(" \U0001F44E El trade fue erroneo. Con delta de : $%.2f" % delta_order)
            self.reset_sell_indicators()
            self.reset_buy_indicators()
        # cash, value = self.broker.get_wallet_balance(COIN_TARGET)
        #amount = value*0.99
        #self.log("Sell ordered: $%.2f. Amount %.6f %s - $%.2f USDT" % (self.data0.close[0],
        #                                                              amount, COIN_TARGET, value), True)
        #return self.sell(size=amount)

    def long(self):
        if self.last_operation == "BUY":
            return

        self.log("Buy ordered: $%.2f" % self.data0.close[0], True)
        self.buy_price_close = self.data0.close[0]
        self.timestamp_buy = self.datetime[0]
        price = self.data0.close[0]

        if ENV == DEVELOPMENT:
            return self.buy()
        
        if ENV == PRODUCTION:
            send_telegram_message(" \U0001F4E3 Orden de compra a : $%.2f" % self.data0.close[0])
            self.last_operation = "BUY"
            self.jsonParser.addBuyOperation(self.timestamp_buy, 
                                self.buy_price_close, 
                                self.buy_price_close, 
                                0, 
                                0)
        #cash, value = self.broker.get_wallet_balance(COIN_REFER)
        #amount = (value / price) * 0.99  # Workaround to avoid precision issues
        #self.log("Buy ordered: $%.2f. Amount %.6f %s. Ballance $%.2f USDT" % (self.data0.close[0],
        #                                                                     amount, COIN_TARGET, value), True)
        #return self.buy(size=amount)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            self.log('ORDER ACCEPTED/SUBMITTED')
            self.order = order
            return

        if order.status in [order.Expired]:
            self.log('BUY EXPIRED', True)

        elif order.status in [order.Completed]:
            if order.isbuy():
                self.last_operation = "BUY"
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm), True)
                self.jsonParser.addBuyOperation(self.timestamp_buy, 
                                                self.buy_price_close, 
                                                order.executed.price, 
                                                order.executed.value, 
                                                order.executed.comm)
                self.reset_buy_indicators()
                if ENV == PRODUCTION:
                    print(order.__dict__)

            else:  # Sell
                self.last_operation = "SELL"
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm), True)
                self.jsonParser.addSellOperation(self.timestamp_sell, 
                                self.sell_price_close, 
                                order.executed.price, 
                                order.executed.value, 
                                order.executed.comm)
                self.reset_sell_indicators()

            # Sentinel to None: new orders allowed
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected: Status %s - %s' % (order.Status[order.status],
                                                                         self.last_operation), True)

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        color = 'green'
        if trade.pnl < 0:
            color = 'red'

        self.jsonParser.addTrade(trade.pnl, trade.pnlcomm)
        self.log(colored('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm), color), True)

    def log(self, txt, send_telegram=False, color=None):
        if not DEBUG:
            return

        value = datetime.now()

        if ENV != PRODUCTION:
            if len(self) > 0:
                value = self.data0.datetime.datetime()

        if color:
            txt = colored(txt, color)

        print('[%s] %s' % (value.strftime("%d-%m-%y %H:%M"), txt))
        if send_telegram:
            send_telegram_message(txt)
