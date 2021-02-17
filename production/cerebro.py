from dataset.data_live import DataLive

class CerebroProduction:
    def __init__(self):
        # self._dolive = False
        # self._doreplay = False
        # self._dooptimize = False
        # self.stores = list()
        # self.feeds = list()
        # self.datas = list()
        # self.datasbyname = collections.OrderedDict()
        self.strats = []
        # self.optcbs = list()  # holds a list of callbacks for opt strategies
        # self.observers = list()
        # self.analyzers = list()
        # self.indicators = list()
        # self.sizers = dict()
        # self.writers = list()
        # self.storecbs = list()
        # self.datacbs = list()
        # self.signals = list()
        # self._signal_strat = (None, None, None)
        # self._signal_concurrent = False
        # self._signal_accumulate = False

        # self._dataid = itertools.count(1)

        self._broker = None
        # self._broker.cerebro = self

        # self._tradingcal = None  # TradingCalendar()

        # self._pretimers = list()
        # self._ohistory = list()
        # self._fhistory = None
        print("Cerebro production inicialized")

    def setbroker(self, broker):
        '''
        Sets a specific ``broker`` instance for this strategy, replacing the
        one inherited from cerebro.
        '''
        self._broker = broker
        self._broker.set_cerebro(self)
        return broker

    def getbroker(self):
        '''
        Returns the broker instance.
        This is also available as a ``property`` by the name ``broker``
        '''
        return self._broker
    

    broker = property(getbroker, setbroker)
    
    def run(self):
        '''
        Start broker live websocket in Binance.
        Return True if ´´broker´´ was configurated previously.
        Return False in otherwise. 
        '''
        if self._broker:
            self._broker.run()
            return True
        return False
    
    def addstrategy(self, strategy, *args, **kwargs):
        '''
        Adds a ``Strategy`` class to the mix for a single pass run.
        Instantiation will happen during ``run`` time.
        args and kwargs will be passed to the strategy as they are during
        instantiation.
        Returns the index with which addition of other objects (like sizers)
        can be referenced
        '''
        self.strategy  = strategy
        return True
    
    def addNextFrame(self, indexData, datetime, open, low, high, close, vloume, next= True):
        '''
        Adds next ``tick``  to strategy.
        For live support only 1 strats. 
        '''
        print(datetime)
        # tick = DataLive(datetime, open, low, high, close)
        # bufferData = []
        # bufferData.append(tick)
        # self.strats[0].datas[0] = tick
        #self.strats[0].datas[indexData].close = [close]
        self.strategy.add_next_frame_live(indexData,datetime, open, low, high, close, vloume, next)
        #self.strats.next()
        # Force next
    def setLenData1(self):
        self.strategy.lendata1 = len(self.strategy.data1.low)

    def getHistoricalData(self, kline_interval, lapse):
        '''
        Set historical data to Cerebro.  
        '''
        self._broker.get_historical_klines(kline_interval, lapse)