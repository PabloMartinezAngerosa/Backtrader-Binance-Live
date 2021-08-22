#TODO:  genera analizis mobiles por ventanas que se mueven en un intervalo. Ejemplo 4 horas cada 15 minutos
# se ejecutan nuevos analizis cada nueca candle de 15 minutos para atras pero de 4 horas.
# se van actualizando las compras y las estimaciones en cual cerrar el high dependiendo del peor estimaciong high/low mean
# funciona para long y para short. 
def generate_expand_candle(unit_candles_list, min_unit, min_expand):
    max = 0
    min = 1000000000
    open = 0
    close = 0
    volume = 0
    for unit_candle in unit_candles_list:
        pass