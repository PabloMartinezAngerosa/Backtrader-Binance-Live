import pygsheets
import pandas as pd
from config import ORDERS_WITH_PRE
#authorization
gc = pygsheets.authorize(service_file='binanceprofit-47ef2982249c.json')

# Create empty dataframe
df = pd.DataFrame()

# Create a column
df['name'] = ['John', 'Steve', 'Sarah']

#open the google spreadsheet (where 'PY to Gsheet Test' is the name of my sheet)

#sh = gc.open('LibertadKamikazeProfitDashboard')

#select the first sheet 

#wks = sh[0]

#update the first sheet with df, starting at cell B2. 
#wks.set_dataframe(df,(1,1))


df = pd.read_csv (r'../dataset/databases/BTCUSDT-1m.csv')



    #order_date = pd.to_datetime(order_date)
    
   # por cada una de las fechas busca la que coinicida con la orden
      # busca el rango de precio stop loss o take profit deacuerdo a la etrategia
         # encuentra hace los calculos y sube al google sheet 


# Deep = 1, solo se permiten dos ordenes simultaneas 1 d short, 1 d long

order_long = {
    "stop_loss" : 0,
    "take_profit" : 0,
    "active": False,
    "date_start" : "",
    "initial": 0,
    "profit" : 0
}

order_short = {
    "stop_loss" : 0,
    "take_profit" : 0,
    "active": False,
    "date_start" : "",
    "initial": 0,
    "profit" : 0
}

acum_capital = 100


row = len(df.index)
for i in range(row):

    datatime = df.iat[i,0]
    open = float(df.iat[i,1])
    high = float(df.iat[i,2])
    low = float(df.iat[i,3])

    for order in ORDERS_WITH_PRE:

        order_type = order["type"]
        order_date = order["date"]
        order_price = order["price"]

        if datatime == order_date:

            if order_type == "LONG" and order_long["active"] == False:

                order_long["active"] = True
                order_long["date_start"] = datatime
                order_long["stop_loss"] = order_price * ( 1 - 0.015 + 0.0045 )
                order_long["take_profit"] = order_price * ( 1.0215 )
                
                if order_short["active"] == True:
                    order_long["initial"] = acum_capital
                    acum_capital = 0
                else:
                    order_long["initial"] = acum_capital/2 
                    acum_capital = acum_capital/2 

                print("se activa la orden tipo long")
                print(order_long)
                break
            
            if order_type == "SHORT" and order_short["active"] == False:

                order_short["active"] = True
                order_short["date_start"] = datatime
                order_short["stop_loss"] = order_price * ( 1  +  (0.015 - 0.0045 ))
                order_short["take_profit"] = order_price * ( 1 - 0.0215 )

                if order_long["active"] == True:
                    order_short["initial"] = acum_capital
                    acum_capital = 0
                else:
                    order_short["initial"] = acum_capital/2 
                    acum_capital = acum_capital/2 

                print("se activa la orden tipo short")
                print(order_short)
                break



    if order_long["active"] == True:

        # succes 
        if open >= order_long["take_profit"] or high >= order_long["take_profit"]:
            print("Orden Long succes  at " + datatime +  " :)")
            order_long["active"] = False
            acum_capital = acum_capital +  ( order_long["initial"] * 1.1075 )
        
        # fail
        if open <= order_long["stop_loss"] or low <= order_long["stop_loss"]:
            print("Orden Long Fail at " + datatime +  " :(")
            order_long["active"] = False
            acum_capital = acum_capital + ( order_long["initial"] * (1 - 0.0525) )
            print(" Long Fail ")
            print(acum_capital)

    if order_short["active"] == True:

        # succes 
        if open <= order_short["take_profit"] or low <= order_short["take_profit"]:
            print("Orden Short succes at " + datatime +  ":)")
            order_short["active"] = False
            acum_capital = acum_capital +  ( order_short["initial"] * 1.1075 )
            print ("Short Succes")
            print(acum_capital)
        
        # fail
        if open >= order_short["stop_loss"] or high >= order_short["stop_loss"]:
            print("Orden Short Fail  at " + datatime +  " :(")
            order_short["active"] = False
            acum_capital = acum_capital +  ( order_short["initial"] * (1 - 0.0525) )
            print ("Short Fail")
            print(acum_capital)


print("Acum Capital Final")
print(acum_capital)
print("total de " + str(len(ORDERS_WITH_PRE)) + " ordenes.")

    