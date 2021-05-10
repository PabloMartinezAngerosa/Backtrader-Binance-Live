from utils import createJsonFile
 
class JsonParser():
    def __init__(self, ensambleIndicators):
        self.data = {}
        self.firstEstimation = False
        self.ticks = []
        self.ticks_average = []
        self.ticks_phemex = []
        self.logs = []
        self.trades = []
        self.sell = None
        self.buy = None
        self.candles  = []
        self.activeCandle = None
        self.inflectionPoints = []
        self.ensambleIndicators = ensambleIndicators
        self.subida_estrepitosa = 0
        self.subida_estrepitosa_buffer = None
        self.subida_estrepitosa_index = 0

    def set_subida_estrepitosa(self, value, index=0):
        self.subida_estrepitosa = value
        self.subida_estrepitosa_index = index

    def set_subida_estrepitosa_buffer(self, scale_ticks, coef, intercept, r_squared, index, delta):
        self.subida_estrepitosa_buffer = {"scale_ticks":scale_ticks, "coef":coef, "intercept":intercept, "r_squared":r_squared, "index":index, "delta":delta}

    def add_strategy_name(self, name):
          self.data["strategyName"] = name

    def addSellOperation(self, timestamp, price, price_executed, amount, commision):
        self.sell = {"timestamp":timestamp,"price":price,"price_executed":price_executed, "amount":amount, "commision":commision}

    def addBuyOperation(self, timestamp, price, price_executed, amount, commision):
        self.buy = {"timestamp":timestamp,"price":price,"price_executed":price_executed, "amount":amount, "commision":commision}
        
    def addTrade(self, pnl, pnlcomn):
        self.trades.append({"sell":self.sell, "buy":self.buy, "pnl":pnl, "pnlcomn":pnlcomn})
    
    def add_inflection_point(self, timestamp, price):
        self.inflectionPoints.append({"time":timestamp, "value":price})

    def addTick(self, date_time, value):
        if self.firstEstimation == True:
            self.ticks.append({"time":date_time, "value":value})
    
    def addTickPhemex(self, date_time, value):
        if self.firstEstimation == True:
            self.ticks_phemex.append({"time":date_time, "value":value})
    
    def add_average_tick(self, date_time, value):
        if self.firstEstimation == True:
            self.ticks_average.append({"time":date_time, "value":value})

    def add_log(self, message, date):
        self.logs.append({"message":message, "date":date})

    def startCandle(self):
        self.activeCandle = {
            "timestamp":self.ensambleIndicators.timestamp,
            "date": self.ensambleIndicators.date.strftime('%B %d, %Y, %r'),
            "estimators": {
                "low":{
                        "media":self.ensambleIndicators.mediaEstimadorLow,
                        "mediaIter2":self.ensambleIndicators.mediaEstimadorLow_iterada2,
                        "mediaIter3":self.ensambleIndicators.mediaEstimadorLow_iterada3,
                        "delta":self.ensambleIndicators.deltaMediaOpenLow
                }, 
                "high":{
                    "media":self.ensambleIndicators.mediaEstimadorHigh,
                    "mediaIter2":self.ensambleIndicators.mediaEstimadorHigh_iterada2,
                    "mediaIter3":self.ensambleIndicators.mediaEstimadorHigh_iterada3,
                    "delta":self.ensambleIndicators.deltaMediaOpenHigh
                },
                "close": {"media": self.ensambleIndicators.mediaEstimadorClose}
            }
        }

    def create_json_file(self, ensambleIndicators):
        self.ensambleIndicators = ensambleIndicators
        if self.firstEstimation == False:
            self.firstEstimation = True
            self.startCandle()
            return True
        else:
            # hace push de los datos de la vela que transcurrio y actualiza el Json
            self.closeCandle()
            self.parseData()
            # crea la proxima con las nuevas estimaciones 
            self.startCandle()
            
    def closeCandle(self):
        # agrega ticks acumulados
        self.activeCandle["ticks"] = self.ticks
        self.activeCandle["averageTicks"] = self.ticks_average
        self.activeCandle["ticksPhemex"] = self.ticks_phemex
        # agrega logs
        self.activeCandle["logs"] = self.logs
        self.activeCandle["inflectionPoints"] = self.inflectionPoints
        self.activeCandle["sbuidaExacerbada"] = self.subida_estrepitosa
        if self.subida_estrepitosa == 1:
            #self.activeCandle["sbuidaExacerbadaBuffer"] = self.subida_estrepitosa_buffer
            self.activeCandle["subidaExacerbadaIndex"] = self.subida_estrepitosa_index
        # agrega ordenes acumuladas
        # agrega invests results generados
        # guarda en candles
        self.candles.append(self.activeCandle)
        # refresh active candle
        self.activeCandle = None
        self.ticks = []
        self.ticks_average = []
        self.ticks_phemex = []
        self.logs = []
        self.inflectionPoints = []
        self.subida_estrepitosa_buffer = None
        self.subida_estrepitosa = 0
        self.subida_estrepitosa_index = 0

    def parseData(self):
        # agrega trades acumulados
        self.data["trades"] = self.trades
        self.data["candles"] = self.candles
        createJsonFile(self.data)

