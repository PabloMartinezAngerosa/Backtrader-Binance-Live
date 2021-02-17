from utils import createJsonFile
 
class JsonParser():
    def __init__(self, ensambleIndicators):
        self.data = {}
        self.firstEstimation = False
        self.ticks = []
        self.candles  = []
        self.activeCandle = None
        self.ensambleIndicators = ensambleIndicators

    def add_strategy_name(self, name):
          self.data["strategyName"] = name

    def addTick(self, date_time, value):
        if self.firstEstimation == True:
            self.ticks.append({"time":date_time, "value":value})

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
        # agrega ordenes acumuladas
        # agrega invests results generados
        # guarda en candles
        self.candles.append(self.activeCandle)
        # refresh active candle
        self.activeCandle = None
        self.ticks = []

    def parseData(self):
        self.data["candles"] = self.candles
        createJsonFile(self.data)

