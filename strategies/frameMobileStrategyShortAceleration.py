# #!/usr/bin/env python3

import backtrader as bt

from config import ENV, PRODUCTION
from strategies.base import StrategyBase
from config import ENV, PRODUCTION, STRATEGY, TESTING_PRODUCTION, LIVE, UPDATE_PARAMS_FUERZA_BRUTA
from strategies.frameMobileStrategyShortAcelerationSubFrame import FrameMobileStrategyShortAcelerationSubFrame

'''

Primera version:
   * hay q llamarlo cada 1 minuto incluso en developer repetido 
   * junta desfasajes de ventanas de 15 minutos cada 1 minuto
   * cuando encuentra condiciones en corto de 15 minutos compra y aguanta cantidades dexageradas.
   * deja un preview a que baje si toca, sube 0.2 o agunta 0.008 aprox

'''
class FrameMobileStrategyShortAceleration(StrategyBase):

    # Moving average parameters
    # params = (('pfast',20),('pslow',50),)

    def __init__(self):
        StrategyBase.__init__(self)
        
        self.ensambleIndicatorsFirstNode = None
        self.long_active = False
        self.short_active = False
        self.is_order_long = False
        self.total_long_orders = ""
        self.total_fial_long = 0
        self.total_succes_long = 0
        self.is_order_short = False
        self.total_short_orders = ""
        self.total_fial_short = 0
        self.total_succes_short = 0
        self.log("Using FrameMobileStrategyShortAceleration strategy")
        self.lendata1 = 0
        self.lagsReady = False
        self.ensambleIndicatorsLags = STRATEGY.get("lags")
        self.ensambleIndicatorsLengthFrames = STRATEGY.get("length_frames")
        self.candle_min = STRATEGY.get("candle_min")
        
        self.total_candle_15_min = 15 # 4 horas se ajusta dinamico buscando media high/low conveniente. Init 4 horas.
        self.total_frame_min = 15   
        
        self.total_subframes = 15 
        #self.dataclose = self.datas[0].close
        self.order = None
        self.len_frames = 0
        self.name = "FrameMobileStrategyLongShort"
        self.subframe_instances =  self.init_subframe_strategy()
        # Instantiate moving averages
        # self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0], 
        #                 period=self.params.pslow)
        # self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0], 
        #                 period=self.params.pfast)
    
    def init_subframe_strategy(self):
        subframe_strategy = []
        for i in range(self.total_candle_15_min):
            print("Add subframe strategy " + str(i))
            subframe_strategy.append(FrameMobileStrategyShortAcelerationSubFrame(i, parent=self))
        return subframe_strategy

    def addNextFrame(self, indexData, datetime, open, low, high, close, volume, next= True, index=0):
        '''
        Adds next ``tick``  to strategy.
        For live support only 1 strats. 
        '''
        self.subframe_instances[index].add_next_frame_live(indexData,datetime, open, low, high, close, volume, next)
    
    def addNextFrameAll(self, indexData, datetime, open, low, high, close, volume, next= True):
        for i in range(self.total_candle_15_min):
            self.addNextFrame(indexData, datetime, open, low, high, close, volume, next, i)

    def next(self):
        # if self.status != "LIVE" and ENV == PRODUCTION:  # waiting for live status in production
        #     return

        if self.order:  # waiting for pending order
            return

        close  = self.datas[0].close[0]
        open = self.datas[0].open[0]
        low = self.datas[0].low[0]
        high = self.datas[0].high[0]
        volume = self.datas[0].volume[0]
        datetime = self.datetime[0]

        actual_price = close

        # envia a todos cada min. 
        self.addNextFrameAll(0,datetime, open, low, high, close, volume, True)
        
        # el precio se va a mandar cada 1 minuto a todas las instancias

        #self.log('Close: %.3f %% '  % close)
        self.jsonParser.addTick(self.datetime[0], actual_price)
        # self.log('Close: %.3f %% '  % float(self.data0.close[-1]))
        
        #  update stategy indicators 
        # self.updateIndicatorsEnsambleLinearModels(self.data0)
        
        if len(self.data1.low) > self.lendata1:
            self.lendata1 += 1
            #if self.lendata1 % self.total_subframes == 0:
            #    print("acumula frame")
            #    self.len_frames += 1
            
            #print("Cada cambio de Vela")
            #print(self.lendata1 % self.total_subframes)
            #print(self.data1.low[0])
            
            low  = self.datas[1].low[0]
            high = self.datas[1].high[0]
            #self.log('Low 1 min tick : %.3f %% '  % low)
            #self.log('High 1 min tick : %.3f %% '  % high)
            #self.log('Low data1: %.3f %% '  % float(self.data1.low[0]))
            #self.log('Low -1 data1: %.3f %% '  % float(self.data1.low[-1]))

            # en produccion ya tiene los datos cargados con historial
            # llama a buscar los indicadores ya estan cargados los lags.
            if ENV == PRODUCTION:
                self.lagsReady = True
            else:
                if ( self.lendata1  >=  self.total_subframes and self.lagsReady == False):
                    self.lagsReady = True
            
            if (self.lagsReady):
                index_candle = int(self.lendata1 % self.total_subframes)
                close = self.datas[1].close[0]
                open = self.datas[1].open[-1*(self.total_candle_15_min -1)]
                max = 0
                min = 1000000000000
                volume = 0
                for i in range(0,-1*self.total_candle_15_min,-1):
                    if self.datas[1].low[i] < min:
                        min = self.datas[1].low[i]
                    if self.datas[1].high[i] > max:
                        max = self.datas[1].high[i]
                    volume = volume + self.datas[1].volume[i]

                #print("Ready para crear y mandar vela de  4 horas a index " + str(index_candle))
                #print("El minimo de la vela es " + str(min))
                #print("El maximo de la vela es " + str(max))
                #print("El open de la vela es " + str(open))
                #print("El close de la vela es " + str(close))
                #print("El volumen total de operaciones es " + str(volume))
                
                # agrega con 1 indica q es cada cambio vela
                #self.cerebro.addNextFrame(1, datetime, open,  low, high, close, volume, False)
                self.addNextFrame(1, datetime, open, min, max, close, volume, False, index_candle)
                # manda el de 4 horas al correspondiente como hace broker
                # cada strategy se encarga de gestionar por si mismo xml y la logica
                # el balance es comun a todos.\




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

