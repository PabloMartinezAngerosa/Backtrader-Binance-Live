from config import STRATEGY, COIN_TARGET, COIN_REFER

MESSAGE_TELEGRAM = {
    "init_session": "Buenas! Se ha lanzado una nueva instancia de trading " + COIN_TARGET + " de velas de " +  
                    str(STRATEGY.get("candle_min")) + 
                    " minutos. Mucha suerte, que siga la aventura. \U0001F680"
}