import subprocess
import json
from dataset.data_live import DataLive
from indicators.ensambleLinearIndicatorsClass import EnsambleLinearIndicatorsClass

class EnsambleLinearRegressionAverage(EnsambleLinearIndicatorsClass):

    def __init__(self, lags=5, length_frames=20):
        self.lags = lags
        self.length_frames = length_frames
        self.indicators = None
    
    def create_lags_json(self, data=None):
        '''
            Asume orden ascendente para generar los lags correspondientes.
            Las filas siempre son el valor en el momento n y los lags correspondientes.
            Ejemplo: close, closeLag1, closeLag2... ; high, highLag1, highLag2...
            Si se quiere tener una ventana de analisis de 20 ticks, rows tiene que ser 20
        '''

        lags_amount = self.lags
        training_frame = self.length_frames

        if len(data.low) < (lags_amount + 1):
            return False
        
        if len(data.low) < (training_frame + 1):
            return False
        
        rows = len(data.low)  - lags_amount
        # crea el objeto json vacio
        jsonData = {"close":[],"low":[],"high":[]}
        for i in range(lags_amount):
            jsonData["closeLag" +  str((i+1))] = []
            jsonData["highLag" +  str((i+1))] = []
            jsonData["lowLag" +  str((i+1))] = []
            jsonData["volLag" +  str((i+1))] = []
        # orden descendente.
        # recorre desde el ultimo menos lags_amount la cantidad de row ascendente
        for i in range(rows + 1):
            index_n = i + lags_amount
            if i < rows:
                value_n = data.close[index_n]
                jsonData["close" ].append(value_n)
                value_n = data.low[index_n]
                jsonData["low" ].append(value_n)
                value_n = data.high[index_n]
                jsonData["high" ].append(value_n)
            else:
                jsonData["close" ].append(0)
                jsonData["low" ].append(0)
                jsonData["high" ].append(0)
            for j in range(lags_amount):
                index_lag =  index_n - (j +  1)
                value_lag = data.close[index_lag]
                jsonData["closeLag" +  str((j+1))].append(value_lag)
                value_lag = data.low[index_lag]
                jsonData["lowLag" +  str((j+1))].append(value_lag)
                value_lag = data.high[index_lag]
                jsonData["highLag" +  str((j+1))].append(value_lag)
                value_lag = data.volume[index_lag]
                jsonData["volLag" +  str((j+1))].append(value_lag)
            # obtiene el valor en el momento n de high, low, close
            # toma desde el indice correspondiente lagas_amount en retroceso 
            # generar closeLag1,closeLag2,... para las varialbes por row
            # hace push. quedan en orden ascendente
        
        # slice rows to frame analysis
        if (len(jsonData["close"]) > (training_frame + 1)):
            cota_inf = len(jsonData["close"]) - (training_frame + 1)
            cota_sup = len(jsonData["close"])
            for j in range(lags_amount):
                jsonData["closeLag" +  str((j+1))] = jsonData["closeLag" +  str((j+1))][cota_inf:cota_sup]
                jsonData["lowLag" +  str((j+1))] = jsonData["lowLag" +  str((j+1))][cota_inf:cota_sup]
                jsonData["highLag" +  str((j+1))] = jsonData["highLag" +  str((j+1))][cota_inf:cota_sup]
                jsonData["volLag" +  str((j+1))] = jsonData["volLag" +  str((j+1))][cota_inf:cota_sup]
            
            jsonData["close" ] = jsonData["close" ][cota_inf:cota_sup]
            jsonData["low" ] = jsonData["low" ][cota_inf:cota_sup]
            jsonData["high" ] = jsonData["high" ][cota_inf:cota_sup]

        return jsonData

    def remix_data_ascen(self, data):
        '''
        Transform ascen data. In Backtrader 
        
        [0]   = n
        [-1] =  n-1
        ...
        [-m] =  n - m

        and we want

        [0] = n-m
        [1]  = n - m + 1
        ...
        [m-1] = n- m + (m-1) = n-1
        [m] = n           
        
        '''
        dataset = DataLive()

        for i in range(len(data.low)):
            index = (i+1) % len(data.low)
            dataset.close.append(data.close[index])
            dataset.low.append(data.low[index])
            dataset.high.append(data.high[index])
            dataset.volume.append(data.volume[index])

        return dataset
    
    def get_indicators(self, dataset):

        indicators = None

        # Define command and arguments
        command ='Rscript'
        path2script ='indicators/R/ensambleLinearModels.R'
        
        dataset = self.remix_data_ascen(dataset)

        values = json.dumps(self.create_lags_json(dataset))
        args = [values.replace('"', '\\"')]

        # Build subprocess command
        cmd = [command, path2script] + args
        
        
        # check_output will run the command and store to result
        try:
            indicators = subprocess.check_output(cmd, universal_newlines=True,shell=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))

        if (indicators):
            self.update(indicators)
       
        return True



