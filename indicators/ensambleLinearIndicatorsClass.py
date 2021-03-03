import math
import pandas as pd

class EnsambleLinearIndicatorsClass():
    
    def __init__(self):
        self.mediaEstimadorLow = None
        self.mediaEstimadorLow_iterada2 = None
        self.mediaEstimadorLow_iterada3 = None
        self.deltaMediaOpenLow = None
        self.mediaEstimadorHigh  = None
        self.mediaEstimadorHigh_iterada2 = None
        self.mediaEstimadorHigh_iterada3 = None
        self.deltaMediaOpenHigh = None
        self.mediaEstimadorClose = None
        self.indicatorsLow = []
        self.indicatorsHigh = []
    
    def updateSqlIndicators(self, sqlRow):
        self.mediaEstimadorLow = sqlRow.low_mean
        self.mediaEstimadorLow_iterada2 = sqlRow.low_mean2
        self.mediaEstimadorLow_iterada3 = sqlRow.low_mean3
        self.deltaMediaOpenLow = sqlRow.low_delta
        self.mediaEstimadorHigh  = sqlRow.high_mean
        self.mediaEstimadorHigh_iterada2 = sqlRow.high_mean2
        self.mediaEstimadorHigh_iterada3 = sqlRow.high_mean3
        self.deltaMediaOpenHigh = sqlRow.high_delta
        self.mediaEstimadorClose = sqlRow.close_mean
        self.timestamp = sqlRow.date
        self.date = pd.to_datetime(self.timestamp, unit='ms')

        self.updateIndicatorsList()

    
    def updateIndicatorsList(self):
        # refresh indicators low and sort
        self.indicatorsLow = []
        self.indicatorsLow.append(self.mediaEstimadorLow)
        self.indicatorsLow.append(self.mediaEstimadorLow_iterada2)
        self.indicatorsLow.append(self.mediaEstimadorLow_iterada3)
        self.indicatorsLow.append(self.deltaMediaOpenLow)
        self.indicatorsLow.sort()

        # refresh indicators high and sort
        self.indicatorsHigh = []
        self.indicatorsHigh.append(self.mediaEstimadorHigh)
        self.indicatorsHigh.append(self.mediaEstimadorHigh_iterada2)
        self.indicatorsHigh.append(self.mediaEstimadorHigh_iterada3)
        self.indicatorsHigh.append(self.deltaMediaOpenHigh)
        self.indicatorsHigh.sort(reverse=True)

    def checkValue(self, value):
        try:
            value = float(value)
            if math.isnan(value):
                return 0
            else:
                return value
        except:
            return 0


    def update(self, encode_values):
        '''
            Recibe los valores codificados por "_" 
            en orden estricto. 
        '''
        values = encode_values.split("_")
        self.mediaEstimadorLow = self.checkValue(values[0])
        self.mediaEstimadorLow_iterada2 = self.checkValue(values[1])
        self.mediaEstimadorLow_iterada3 = self.checkValue(values[2])
        self.deltaMediaOpenLow = self.checkValue(values[3])
        self.mediaEstimadorHigh  = self.checkValue(values[4])
        self.mediaEstimadorHigh_iterada2 = self.checkValue(values[5])
        self.mediaEstimadorHigh_iterada3 = self.checkValue(values[6])
        self.deltaMediaOpenHigh = self.checkValue(values[7])
        self.mediaEstimadorClose = self.checkValue(values[8])

        self.updateIndicatorsList()
    



        

