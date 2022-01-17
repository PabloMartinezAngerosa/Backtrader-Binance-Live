import pygsheets
import pandas as pd
from config import ORDERS_WITH_PRE, ORDERS_COMPLETE
#authorization

gc = pygsheets.authorize(service_file='binanceprofit-47ef2982249c.json')
sh = gc.open('LibertadKamikazeProfitDashboard')
wks = sh[0]


LEVERAGE = "x14"

def setGoogleSheetOrder(order_type, order, acum_capital, status):
    # get rows number
    # add new row
    list_rows_col = wks.get_col(1)   # Returns a list of all values in a column
    print("total de columnas " + str(len(list_rows_col)))
    NEXT_ROW_INDEX = len(list_rows_col) + 1
    next_row_index = NEXT_ROW_INDEX
    wks.add_rows(1)     # Add  n rows to worksheet at end
    # Order Type
    #wks.update_value('A' + str(next_row_index), order_type) 
    # Entry price
    #wks.update_value('B' + str(next_row_index), order["entry_price"])  
    # Exit price
    #wks.update_value('C' + str(next_row_index), order["exit_price"])  
    # Stop Loss
    #wks.update_value('D' + str(next_row_index), order["stop_loss"])  
    # Take profit
    #wks.update_value('E' + str(next_row_index), order["take_profit"]) 
    # Leverage
    #wks.update_value('F' + str(next_row_index), LEVERAGE) 
    # Initial Amount
    #wks.update_value('G' + str(next_row_index), order["initial"]) 
    # Status
    #wks.update_value('H' + str(next_row_index), status) 
    # Balance
    #wks.update_value('I' + str(next_row_index), acum_capital) 
    # Date Start 
    #wks.update_value('J' + str(next_row_index), order["date_start"])
    # Date End 
    #wks.update_value('K' + str(next_row_index), order["date_end"])

    wks.update_row(next_row_index , [
        order_type,
        order["entry_price"],
        order["exit_price"],
        order["stop_loss"],
        order["take_profit"],
        LEVERAGE,
        order["initial"],
        status,
        acum_capital,
        order["date_start"],
        order["date_end"]
        ]
    )


# Create empty dataframe
#df = pd.DataFrame()

# Create a column
#df['name'] = ['John', 'Steve', 'Sarah']

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
    "entry_price":0,
    "exit_price":0,
    "stop_loss" : 0,
    "take_profit" : 0,
    "active": False,
    "date_start" : "",
    "date_end" : "",
    "initial": 0,
    "balance" : 0
}

order_short = {
    "entry_price":0,
    "exit_price":0,
    "stop_loss" : 0,
    "take_profit" : 0,
    "active": False,
    "date_start" : "",
    "date_end" : "",
    "initial": 0,
    "balance" : 0
}

acum_capital = 100

# set orders strategy ORDERS_COMPLETE ORDERS_WITH_PRE
ORDERS = ORDERS_WITH_PRE

### WITH PRE LIMIT ####



# X10 ordes with pre / acum final 187.05
#profit_percent = 0.022
#roe_succes = 0.21
#roe_fail = 0.105


# X14 ordes with pre / 235.4758626
profit_percent = 0.0225
roe_succes = 0.2961
roe_fail = 0.147

# X18 ordes with pre / acum final  289.73
#profit_percent = 0.023
#roe_succes = 0.3807
#roe_fail = 0.1891

#### WITHOUT LIMIT #### 

# X5 ordes without pre limit acum final 41.073343561379886
#profit_percent = 0.03
#roe_succes = 0.1506
#roe_fail = 0.0751

# X10 ordes without pre limit acum final 31.13720186014597
#profit_percent = 0.0303
#roe_succes = 0.30399
#roe_fail = 0.1501





row = len(df.index)
for i in range(row):

    datatime = df.iat[i,0]
    open = float(df.iat[i,1])
    high = float(df.iat[i,2])
    low = float(df.iat[i,3])

    for order in ORDERS:

        order_type = order["type"]
        order_date = order["date"]
        order_price = order["price"]

        if datatime == order_date:

            if order_type == "LONG" and order_long["active"] == False  and order_short["active"] == False:

                order_long["active"] = True
                order_long["date_start"] = datatime
                order_long["stop_loss"] = order_price * ( 1 - 0.015 + 0.0045 )
                order_long["take_profit"] = order_price * ( 1 + profit_percent )
                
                if order_short["active"] == True:
                    order_long["initial"] = acum_capital
                    acum_capital = 0
                else:
                    order_long["initial"] = acum_capital
                    acum_capital = 0
                    #order_long["initial"] = acum_capital/2 
                    #acum_capital = acum_capital/2 

                #print("se activa la orden tipo long")
                #print(order_long)
                break
            
            if order_type == "SHORT" and order_short["active"] == False and order_long["active"] == False:

                order_short["active"] = True
                order_short["date_start"] = datatime
                order_short["stop_loss"] = order_price * ( 1  +  (0.015 - 0.0045 ))
                order_short["take_profit"] = order_price * ( 1 - profit_percent)

                if order_long["active"] == True:
                    order_short["initial"] = acum_capital
                    acum_capital = 0
                else:
                    order_short["initial"] = acum_capital
                    acum_capital = 0
                    #order_short["initial"] = acum_capital/2 
                    #acum_capital = acum_capital/2 

                #print("se activa la orden tipo short")
                #print(order_short)
                break



    if order_long["active"] == True:

        # succes 
        if open >= order_long["take_profit"] or high >= order_long["take_profit"]:
            print("Orden Long succes  at " + datatime +  " :)")
            order_long["active"] = False
            order_long["date_end"] = datatime
            acum_capital = acum_capital +  ( order_long["initial"] * (1 + roe_succes) )
            setGoogleSheetOrder("LONG", order_long, acum_capital, "succes")
        
        # fail
        if open <= order_long["stop_loss"] or low <= order_long["stop_loss"]:
            print("Orden Long Fail at " + datatime +  " :(")
            order_long["active"] = False
            order_long["date_end"] = datatime
            acum_capital = acum_capital + ( order_long["initial"] * (1 - roe_fail) )
            setGoogleSheetOrder("LONG", order_long, acum_capital, "fail")
            #print(" Long Fail ")
            #print(acum_capital)

    if order_short["active"] == True:

        # succes 
        if open <= order_short["take_profit"] or low <= order_short["take_profit"]:
            print("Orden Short succes at " + datatime +  ":)")
            order_short["active"] = False
            order_short["date_end"] = datatime
            acum_capital = acum_capital +  ( order_short["initial"] * (1 + roe_succes) )
            setGoogleSheetOrder("SHORT", order_short, acum_capital, "succes")
            #print ("Short Succes")
            #print(acum_capital)
        
        # fail
        if open >= order_short["stop_loss"] or high >= order_short["stop_loss"]:
            print("Orden Short Fail  at " + datatime +  " :(")
            order_short["active"] = False
            order_short["date_end"] = datatime
            acum_capital = acum_capital +  ( order_short["initial"] * (1 - roe_fail) )
            setGoogleSheetOrder("SHORT", order_short, acum_capital, "fail")
            #print ("Short Fail")
            #print(acum_capital)


print("Acum Capital Final")
print(acum_capital)
print("total de " + str(len(ORDERS)) + " ordenes.")
