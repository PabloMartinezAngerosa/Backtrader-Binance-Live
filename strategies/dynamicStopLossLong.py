# #!/usr/bin/env python3

import backtrader as bt

from config import ENV, PRODUCTION
from strategies.base import StrategyBase


class DynamicStopLossLong(StrategyBase):

    # Moving average parameters
    # params = (('pfast',20),('pslow',50),)

    def __init__(self):
        StrategyBase.__init__(self)

        self.log("Using Dynamic Stop Loss Long strategy")
        self.lendata1 = 0
        self.order = None
        self.name = "DynamicStopLossLong"

        self.indicators_ready = False
        # Cuanto permite correrse de la estimacion
        # antes de ejecutar el trade.
        self.delta_stop_loss_low = 25 
        self.delta_stop_loss_high = 25  

        self.hit_high_prediction = False
        self.stop_loss_low_active = False
        self.stop_loss_low = 0.0
        self.active_low_prediction = 0.0
        self.stop_loss_high_active = False
        self.stop_loss_high = 0.0
        self.active_high_prediction = 0.0
        self.orderActive  = False



    def next(self):
        # if self.status != "LIVE" and ENV == PRODUCTION:  # waiting for live status in production
        #     return

        if self.order:  # waiting for pending order
            return

        close  = self.datas[0].close[0]
        self.log('Close: %.3f %% '  % close)
        # self.log('Close: %.3f %% '  % float(self.data0.close[-1]))
        
        # update stategy indicators 
        self.updateIndicatorsEnsambleLinearModels(self.data1)
        
        if len(self.data1.low) > self.lendata1:


            print("Low")
            print(self.data1.low[0])
            self.lendata1 += 1
            low  = self.datas[1].low[0]
            high = self.datas[1].high[0]
            self.log('Low 1 min tick : %.3f %% '  % low)
            self.log('High 1 min tick : %.3f %% '  % high)
            self.log('Low data1: %.3f %% '  % float(self.data1.low[0]))
            self.log('Low -1 data1: %.3f %% '  % float(self.data1.low[-1]))

        # Check if we are in the market
        # if not self.position:
        #     # We are not in the market, look for a signal to OPEN trades
            
        #     #If the 20 SMA is above the 50 SMA
        #     if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] < self.slow_sma[-1]:
        #         self.log(f'BUY CREATE {self.dataclose[0]:2f}')
        #         # Keep track of the created order to avoid a 2nd order
        #         self.order = self.buy()
        #     #Otherwise if the 20 SMA is below the 50 SMA   
        #     elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
        #         self.log(f'SELL CREATE {self.dataclose[0]:2f}')
        #         # Keep track of the created order to avoid a 2nd order
        #         self.order = self.sell()
        # else:
        #     # We are already in the market, look for a signal to CLOSE trades
        #     if len(self) >= (self.bar_executed + 5):
        #         self.log(f'CLOSE CREATE {self.dataclose[0]:2f}')
        #         self.order = self.close()

