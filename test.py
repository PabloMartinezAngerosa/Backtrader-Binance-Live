from strategies.elasticLowBandOverlapHighFuerzaBruta import ElasticLowBandOverlapHighFuerzaBruta
import time
from multiprocessing import Pool
from config import SANDBOX_INITAL_CAPITAL
import asyncio

#asyncio.run(main())

def multi_core_action(index):
    elasticFuerzaBruta = ElasticLowBandOverlapHighFuerzaBruta()
    return elasticFuerzaBruta.get_best_estrategy_params_all(1615788000109, 1615788900065, index)

def get_best_values():
    s = time.perf_counter()
    p = Pool(4)
    values_multicore = p.map(multi_core_action, [0,1,2,3])
    max_balance = []
    for cores in values_multicore:
        max_balance.append(cores["max"])
    max_balance = max(max_balance)
    print("El valor maximo es " + str(max_balance))

    stoploss = []
    cota_superior_low = []
    elastic_margin_low = []
    fixed_limit_high = []
    minimum_profit_proyected = []
    mean_filter_lag = []
    touch_high_cota = []


    for cores in values_multicore:
        fields = cores["values"]
        for result in fields:
            if result["balance"] == max_balance:
                stoploss.append(result["stoploss"])
                cota_superior_low.append(result["cota_superior_low"])
                elastic_margin_low.append(result["elastic_margin_low"])
                fixed_limit_high.append(result["fixed_limit_high"])
                minimum_profit_proyected.append(result["minimum_profit_proyected"])
                mean_filter_lag.append(result["mean_filter_lag"])
                touch_high_cota.append(result["touch_high_cota"])
    
    optimal_values =  {
        "stoploss" : sum(stoploss)/len(stoploss),
        "cota_superior_low" : sum(cota_superior_low)/len(cota_superior_low),
        "elastic_margin_low" : sum(elastic_margin_low)/len(elastic_margin_low),
        "fixed_limit_high" : sum(fixed_limit_high)/len(fixed_limit_high),
        "minimum_profit_proyected" : sum(minimum_profit_proyected)/len(minimum_profit_proyected),
        "mean_filter_lag" : sum(mean_filter_lag)/len(mean_filter_lag),
        "touch_high_cota" : sum(touch_high_cota)/len(touch_high_cota)
    }
                
    print("Con un capital inicial de " + str(SANDBOX_INITAL_CAPITAL) + " el retorno maximo final es de " + str(max_balance))
    print(optimal_values)
    elapsed = time.perf_counter() - s
    print(f"{__file__} executed in {elapsed:0.2f} seconds.")

if __name__ == "__main__":
    print("Before async")
    #asyncio.run(get_best_values())
    get_best_values()
    print("end code!!!!")