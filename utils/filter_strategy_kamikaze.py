strategy = "FTTTFTFTFTFFTFFFFTFTFTTFTTTFTTTFFFTTFFTTFFFTFTTFFFFTFFTFTTTFFTFFFTFFTTTTFFFFFFFTTFFTTFFTFTFFFTTFTFTTFFTTTFFTFFTFTTFTFTFTTFFFTTFTFFTFTFTFTTFFTTFFFFTFTTFFFFFTFTTFFFFFTFFFFTTFTTFTTFTTFFFTTTFTFFTTTTTFTFFTTFTFTFFFTTFFTFTTFTFTFTTTTTFFTFTTTTFFFTFTTTTFFFTFTTTFFTTTFTTFFFTTFFFTFFTFFFFFTFTFTFTFTFTTTFFFFFTFTTTTTFFTTTFFTTTFFTFTTFTFTTTFTTFFFFFTTFFFTFTTFTFTFFFTFTFFTFTFTFFTFTFTFFFFTTFTFTFFTFTTTTTFFFFFTTTFFFTFTTFFFFFFFTFTFFTFFTFFFFTTTFFFFFTFTTTFFTTFFFTTTTTTFFFTFTFTFFFFTTFFTTFFFFFTFTFFTTFTFTTFFFFTFFFTTFTFTTFFFFTFTFTFTTFTFFTFTFTFFTTFFFFFTFTFFFTFFTTFTFFTTTFTTFFFTTTFTFTFTFFFTTFFFFFFTFTFFFFTTTTFTTTTTFFFFTFFFTFTTFFFTTTFFTTTFFTFTFFTFTTTTTFFFTFFFFFTFFTTFTTFFTTTFTTTFTFFTTTTFFFFFTTFTTFTFTFFFFTFTFTTTFFTFFTTFFFTTTFTTTTFTTTFTFFFFFFTTTTFTFFFFFTTFFFTFTTTFFFTFFFFFFTTFTFFFTFFFTFTTFFTFTFTTFTTTTTTFTFTFFTFFFTFTFTFFFTFFTFTFTFTFFFTFTTTTFFTFFFTTTTFFTFTTFFTFFFTFFTFFTFFFTFFTFFFFFFTTTTFFFFFTTFFFFFTFFFTFFFTTTTFTFTFFFFTFTFFFFTTFFTFTFTFTFFFFTTFFFTTFTTFTTFTFFFFTFTTTFFFFFTFFTFTFFTTTFFTTTTTFTFTFFTTFTTTTTFFTTFTTTFFFTFFFFTFTTFTTFFFTTFFFFTFFTTFFFTFFFTTTTTFFFTFTTTFTFTFFFFTTFFTTFFTFTFTTFTTFFFTTTFTTFTTFFFTTTFFTFFTTTFFFFFTFFFTFFFFFTFTFTTFTTTFTTTTTFTFTF"


make_long = False
counter_f = 0

make_short = False
counter_t = 0

orders_final = ""

for order_status in strategy:
    if order_status == "T":
        # to TFFFFF Long
        counter_f = 0
        if make_long == True:
            print("Succes! TFFFFFT")
            orders_final += "T"
            make_long = False

        # to FTTTTT short
        counter_t += 1

        if counter_t == 5:
            make_short = True

        if counter_t == 6:
            make_short = False
            print("Fail :( FTTTTT")
            orders_final += "f"

    if order_status == "F":
        # to TFFFFF Long
        counter_f += 1

        if counter_f == 5:
            make_long = True

        if counter_f == 6:
            make_long = False
            print("Fail :( TFFFFFF")
            orders_final += "F"
        
        
        # to FTTTTT short
        counter_t = 0
        if make_short == True:
            print("Succes! FTTTTT")
            orders_final += "t"
            make_short = False


print(orders_final)  


total_t = 0
total_f = 0

for order_result in orders_final:
    if order_result == "T":
        total_t = total_t + 1
    elif order_result == "F":
        total_f = total_f + 1
         
print("El total True es " + str(total_t))
print("El total False es " + str(total_f))


