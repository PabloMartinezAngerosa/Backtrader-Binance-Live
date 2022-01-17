
strategy = "FTFFFFFTTTFFTFFFFTTFFTFTFTFTFFFFTTFTTFFTTFFTTFFFFFFTTTTTFFFTFFFFTFTFFTTTTFFTFTTFFFFFTFFFTTTFTTFF"

index = 0
orders_a = ""
orders_b = ""
orders_c = ""
orders_d = ""
orders_e = ""

for order in strategy:
    index += 1
    if index%5 == 0 :
        orders_a += order
    elif index%5 == 1:
        orders_b += order
    elif index%5 == 2:
        orders_c += order
    elif index%5 == 3:
        orders_d += order
    elif index%5 == 4:
        orders_e += order

print("order a " + orders_a)
print("order b " + orders_b)
print("order c " + orders_c)
print("order d " + orders_d)
print("order e " + orders_e)

# filter
def filter_TFX5(strategy):
    order_filtered = ""
    index = -1
    for order_status in strategy:
        index += 1
        if index > 6 and index < (len(strategy)-5):
            if strategy[index-1] == "F" and strategy[index-2] == "F" and strategy[index-3] == "F" and strategy[index-4] == "F" and strategy[index-5] == "F"  and strategy[index-6] == "T":
                order_filtered += strategy[index]
    return order_filtered

def filter_TFX1(strategy):
    order_filtered = ""
    index = -1
    for order_status in strategy:
        index += 1
        if index > 2 and index < (len(strategy)):
            if strategy[index-1] == "F" and strategy[index-2] == "T":
                order_filtered += strategy[index]
    return order_filtered

#strategy = filter_TFX1(strategy)
print(strategy)

active = "T"
orders_inverse = ""
total_succes = 0
total_fail = 0
for order_result in strategy:
    if active == order_result :
        orders_inverse += "T"
        if active == "T":
            total_succes += 1
        else:
            total_succes += 1
    else:
        orders_inverse += "F"
        if active == "T":
            total_fail += 1
        else:
            total_fail += 1 
        if active == "T":
            active = "F"
        else:
            active = "T"

total_t = 0
total_f = 0
print("total inverse succes " + str(total_succes) + " total fail " + str(total_fail))
print("Orders inverse es " + orders_inverse)

for order_result in orders_inverse:
    if order_result == "T":
        total_t = total_t + 1
    else:
        total_f = total_f + 1
         
print("El total True es " + str(total_t))
print("El total False es " + str(total_f))



# simulate strategy
# hacer purebas de test !!! maniana urgente !!!


def generate_succes(index, order_type):
    index_range = 2**index
    orders = ""
    for i in range(index_range):
        orders += order_type
    return orders

def generate_acum_fails(index, order_type):
    orders = ""
    for i in range(index):
        for j in range(2**i):
            orders += order_type
    return orders

succes = 0.01
fail = 0.0027
capital = 0
leverage = 10


t_sequence = 0
t_sequence_b = 0
orders_final = ""
max_t_secuence = 0

for order_status in strategy:
    if order_status == "T":
        t_sequence += 1
        t_sequence_b += 1
        if  t_sequence == 12:
            orders_final += generate_acum_fails(t_sequence,"T")
            t_sequence = 0
        #if  t_sequence_b == 10+4:
        #    #orders_final += generate_acum_fails(t_sequence_b-4,"F")
        #    t_sequence_b = 0
    else:
        if t_sequence > max_t_secuence:
            max_t_secuence = t_sequence
        orders_final += generate_acum_fails(t_sequence,"T") + generate_succes(t_sequence,"F")
        #if t_sequence_b >= 4:
        #orders_final += generate_acum_fails(t_sequence_b-4,"F") + generate_succes(t_sequence_b-4,"T")
        t_sequence = 0
        #t_sequence_b = 0

print("El total ordes resultante  es " + orders_final)
print("El maximo de T es " + str(max_t_secuence))

total_t = 0
total_f = 0

for order_result in orders_final:
    if order_result == "T":
        total_t = total_t + 1
    elif order_result == "F":
        total_f = total_f + 1
         
print("El total True es " + str(total_t))
print("El total False es " + str(total_f))







