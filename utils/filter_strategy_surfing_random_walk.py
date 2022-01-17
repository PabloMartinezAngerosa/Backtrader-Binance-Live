strategy = "FFTFTFFTTFFFFFFTFTFFFFFTTFFTTFFTTTFTTTFTTFFTTFFTFTFFTFTFTTFTTTFFFTFFTFFTFTFTFFTFFFFFFFTTFFFFFFTFFTTTTFFTFFFTFFTTTTFTTFFFTFFTTFTTTTFTTTTFTFTTTFTFFTFFTTFTTTFFTTFFTTFFTF"

t_sequence = 0
orders_final = ""
max_t_secuence = 0
profit = 0

def return_MG_profit(index):
    if index == 0:
        return 4.2
    elif index == 1:
        return 6.51
    elif index == 2:
        return 10.71
    elif index == 3:
        return 17.556
    elif index == 4:
        return 28.329
    elif index == 5:
        return 46.284
    elif index == 6:
        return 75.81

for order_status in strategy:
    if order_status == "T":
        t_sequence += 1
    else:
        if t_sequence > max_t_secuence:
            max_t_secuence = t_sequence
        profit += return_MG_profit(t_sequence)
        t_sequence = 0

print("El total profit resultante  es " + str(profit))
print("El maximo de T es " + str(max_t_secuence))


counter = 0
new_strategy = ""
for order_status in strategy:
    counter += 1
    if counter == 8:
        counter = 0
        if order_status == "T":
            new_strategy += "F"
        elif order_status == "F":
            new_strategy += "T"
    else:
        new_strategy += order_status

print(new_strategy)
