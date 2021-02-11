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
    
    def update(self, encode_values):
        '''
            Recibe los valores codificados por "_" 
            en orden estricto. 
        '''
        values = encode_values.split("_")
        self.mediaEstimadorLow = float(values[0])
        self.mediaEstimadorLow_iterada2 = float(values[1])
        self.mediaEstimadorLow_iterada3 = float(values[2])
        self.deltaMediaOpenLow = float(values[3])
        self.mediaEstimadorHigh  = float(values[4])
        self.mediaEstimadorHigh_iterada2 = float(values[5])
        self.mediaEstimadorHigh_iterada3 = float(values[6])
        self.deltaMediaOpenHigh = float(values[7])
        self.mediaEstimadorClose = float(values[8])

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
        self.indicatorsHigh.append(self.mediaEstimadorLow_iterada3)
        self.indicatorsHigh.append(self.deltaMediaOpenHigh)
        self.indicatorsHigh.sort(reverse=True)


        

